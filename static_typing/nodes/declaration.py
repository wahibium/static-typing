"""Declaration nodes, i.e. Assign and AnnAssign."""

import ast
import collections
import logging

import typed_ast.ast3

from .statically_typed import StaticallyTyped

_LOG = logging.getLogger(__name__)


def create_statically_typed_declaration(ast_module):

    class StaticallyTypedDeclarationClass(StaticallyTyped[ast_module]):

        _type_fields = ('vars',)

        def __init__(self, *args, **kwargs):
            self._vars = collections.OrderedDict()
            super().__init__(*args, **kwargs)

        def _add_declaration(self, target, type_hint):
            if isinstance(target, ast_module.Tuple):
                if type_hint is None:
                    type_hint = [None for _ in target.elts]
                if isinstance(type_hint, ast_module.AST):
                    raise TypeError(f'unresolved type hint: {ast_module.dump(type_hint)}')
                if not isinstance(type_hint, collections.abc.Iterable):
                    raise TypeError(
                        f'expected iterable type hint but got {type(type_hint)}: {type_hint}')
                for elt, elt_hint in zip(target.elts, type_hint):
                    self._add_declaration(elt, elt_hint)
                return
            self._vars[target] = type_hint

        def _add_declarations(self, targets, type_hint):
            if len(targets) == 1:
                self._add_declaration(targets[0], type_hint)
            for target in targets:
                self._add_declaration(target, type_hint)

    return StaticallyTypedDeclarationClass


StaticallyTypedDeclaration = {ast_module: create_statically_typed_declaration(ast_module)
                              for ast_module in (ast, typed_ast.ast3)}


def create_statically_typed_assign(ast_module):

    class StaticallyTypedAssignClass(ast_module.Assign, StaticallyTypedDeclaration[ast_module]):

        def _add_type_info(self):
            self._add_declarations(self.targets, getattr(self, 'type_comment', None))

    return StaticallyTypedAssignClass


StaticallyTypedAssign = {ast_module: create_statically_typed_assign(ast_module)
                         for ast_module in (ast, typed_ast.ast3)}


def create_statically_typed_ann_assign(ast_module):

    class StaticallyTypedAnnAssignClass(
            ast_module.AnnAssign, StaticallyTypedDeclaration[ast_module]):

        def _add_type_info(self):
            self._add_declaration(self.target, self.annotation)

    return StaticallyTypedAnnAssignClass


StaticallyTypedAnnAssign = {ast_module: create_statically_typed_ann_assign(ast_module)
                            for ast_module in (ast, typed_ast.ast3)}