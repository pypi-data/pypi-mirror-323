import logging
import sys
from pathlib import Path
import subprocess
import uuid
from string import Template

from typing import List, Set, Optional

import EVMVerifier.certoraContextAttributes as Attrs
from EVMVerifier.certoraContextClass import CertoraContext
from Shared import certoraUtils as Util

scripts_dir_path = Path(__file__).parent.resolve()
sys.path.insert(0, str(scripts_dir_path))

split_rules_logger = logging.getLogger("split_rules")


class SplitRulesHandler():
    context: CertoraContext
    all_rules: Optional[Set[str]] = None
    split_rules: Optional[Set[str]] = None
    rest_rules: Optional[Set[str]] = None

    def __init__(self, context: CertoraContext):
        if not context:
            raise ValueError("SplitRulesHandler: context must be set")
        SplitRulesHandler.context = context

    def generate_runs(self) -> int:
        self.all_rules = self.get_cvl_rules()
        assert len(self.all_rules) > 0, "generate_runs: all rules were filtered out"
        self.split_rules = self.get_cvl_rules(True)
        self.rest_rules = self.all_rules - self.split_rules
        return self.run_commands()

    def get_cvl_rules(self, split_rules: bool = False) -> Set[str]:
        def jar_list_value(list_attr: List[str]) -> str:
            return ','.join(list_attr)

        path_to_typechecker = Util.find_jar("Typechecker.jar")

        command = ["java", "-jar", str(path_to_typechecker), "-listRules", "-buildDirectory", str(Util.get_build_dir())]

        if self.context.exclude_rule:
            command += ['-excludeRule', jar_list_value(self.context.exclude_rule)]

        if not split_rules and self.context.rule:
            command += ['-rule',  jar_list_value(self.context.rule)]
        elif split_rules and self.context.split_rules:
            command += ['-rule', jar_list_value(self.context.split_rules)]
        try:

            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return set(result.stdout.strip().split("\n"))

        except subprocess.CalledProcessError as e:
            raise Util.CertoraUserInputError(f"Failed to get {'split ' if split_rules else ''}rules\ncommand: {command}\n{e}")

    def run_commands(self) -> int:
        rule_flag = Attrs.EvmProverAttributes.RULE.get_flag()
        split_rules_flag = Attrs.EvmProverAttributes.SPLIT_RULES.get_flag()
        msg_flag = Attrs.CommonAttributes.MSG.get_flag()
        group_id_flag = Attrs.EvmProverAttributes.GROUP_ID.get_flag()
        disable_local_typechecking_flag = Attrs.EvmProverAttributes.DISABLE_LOCAL_TYPECHECKING.get_flag()

        def remove_rule_flags_from_cli() -> List[str]:
            # any --rule flag should be removed from CLI during splitting, since it is set during the split
            new_cli = []
            skip = False
            for item in self.context.args_list:
                if item.startswith(rule_flag) or item.startswith(split_rules_flag):
                    skip = True
                elif item.startswith('--') and skip:
                    skip = False
                if not skip:
                    new_cli.append(item)
            return new_cli

        def get_cmd() -> str:
            assert Attrs.is_evm_app(), "Split rules is supported only for EVM apps"
            if hasattr(self.context, 'prover_cmd'):
                return self.context.prover_cmd
            if self.context.local:
                return Util.CERTORA_RUN_SCRIPT
            return Util.CERTORA_RUN_APP

        def generate_prover_calls() -> List[List[str]]:
            cli_commands = []
            args = remove_rule_flags_from_cli()
            if not self.context.group_id:
                self.context.group_id = str(uuid.uuid4())

            if not self.context.msg:
                self.context.msg = ''
            msg_template = Template(f"{self.context.msg} (Rule: $rule)")

            cmd = [get_cmd()] + args + [group_id_flag, self.context.group_id, disable_local_typechecking_flag,
                                        split_rules_flag]

            if self.split_rules:
                for rule in self.split_rules:
                    cli_commands.append(cmd + [rule_flag, rule, msg_flag, msg_template.substitute(rule=rule)])
            if self.rest_rules:
                cli_commands.append(cmd + [rule_flag] + list(self.rest_rules) +
                                    [msg_flag, 'all rules not defined in split_rules or in exclude_rule'])
            return cli_commands

        prover_calls = generate_prover_calls()
        if self.context.test == str(Util.TestValue.AFTER_RULE_SPLIT):
            raise Util.TestResultsReady(prover_calls)

        processes = []
        # Start all processes
        for command in prover_calls:
            split_rules_logger.debug(f"Running {' '.join(command)}")
            processes.append(subprocess.Popen(command))

        # Wait for all processes to complete and collect return codes
        return_codes = [p.wait() for p in processes]

        return_value = 0
        for i, return_code in enumerate(return_codes):
            if return_code != 0:
                split_rules_logger.debug(f"Process {i} failed with exit code {return_code}")
                return_value = 1

        return return_value
