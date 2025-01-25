#-----------------------------------------------------------------
# pycparser: func_defs_add_param.py
#
# Example of rewriting AST nodes to add parameters to function
# definitions. Adds an "int _hidden" to every function.
#
# Eli Bendersky [https://eli.thegreenplace.net/]
# License: BSD
#-----------------------------------------------------------------
import sys

sys.path.extend(['.', '..'])

from pycparser import c_ast, c_generator, c_parser

text = r"""
void foo(int a, int b) {
}

void bar() {
}
"""


class ParamAdder(c_ast.NodeVisitor):
    def visit_FuncDecl(self, node) -> None:
        ty = c_ast.TypeDecl(declname='_hidden',
                            quals=[],
                            align=[],
                            type=c_ast.IdentifierType(['int']))
        newdecl = c_ast.Decl(
                    name='_hidden',
                    quals=[],
                    align=[],
                    storage=[],
                    funcspec=[],
                    type=ty,
                    init=None,
                    bitsize=None,
                    coord=node.coord)
        if node.args:
            node.args.params.append(newdecl)
        else:
            node.args = c_ast.ParamList(params=[newdecl])


if __name__ == '__main__':
    parser = c_parser.CParser()
    ast = parser.parse(text)
    ast.show(offset=2)

    v = ParamAdder()
    v.visit(ast)

    ast.show(offset=2)

    generator = c_generator.CGenerator()
