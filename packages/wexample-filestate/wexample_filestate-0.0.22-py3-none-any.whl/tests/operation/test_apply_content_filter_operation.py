from typing import Optional

from wexample_config.config_value.filter.trim_config_value_filter import TrimConfigValueFilter
from wexample_config.const.types import DictConfig
from wexample_filestate.config_option.children_config_option import ChildrenConfigOption
from wexample_filestate.testing.test_abstract_operation import TestAbstractOperation
from wexample_helpers.helpers.file import file_read


class TestContentApplyContentFilterOperation(TestAbstractOperation):
    missing_file_name: str = 'simple-readme.md'

    def _operation_test_setup_configuration(self) -> Optional[DictConfig]:
        return {
            "children": ChildrenConfigOption(value=[
                {
                    "name": "trim-text.txt",
                    "type": "file",
                    "content_filter": TrimConfigValueFilter
                }
            ], parent=self.state_manager)
        }

    def _operation_get_count(self) -> int:
        return 1

    def _operation_test_assert_initial(self) -> None:
        assert self.state_manager.dump() == {
            'name': 'resources',
            'children': [
                {
                    'name': 'trim-text.txt',
                    'type': 'file',
                    'content_filter': "filters=[','.join(filters_names)]"
                }
            ]
        }

        text = file_read(self.state_manager.find_by_name('trim-text.txt').get_resolved())
        assert text.startswith("\n") and text.endswith("\n")

    def _operation_test_assert_applied(self):
        assert file_read(self.state_manager.find_by_name('trim-text.txt').get_resolved()) == "THIS IS A TRIM TEXT"
