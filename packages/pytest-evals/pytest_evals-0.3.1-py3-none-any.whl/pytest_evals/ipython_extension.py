# pragma: exclude file
import shlex
from pathlib import Path

try:
    from IPython.core.magic import Magics, magics_class, cell_magic  # type: ignore
except ImportError:

    def magics_class(cls):
        pass

    class Magics:
        def __init__(self, shell):
            pass

    def cell_magic(func):
        pass


@magics_class
class EvalsMagics(Magics):
    def __init__(self, shell):
        super().__init__(shell)
        try:
            import ipytest

            ipytest.autoconfig(
                run_in_thread=True,  # pyright: ignore [reportArgumentType]
                addopts=[  # pyright: ignore [reportArgumentType]
                    "--assert=plain",
                    "-s",  # Don't capture output
                    "--log-cli-level=ERROR",
                ],
            )
        except ImportError:
            raise ImportError(
                "⚠️ `ipytest` is required to use `pytest-evals` in notebooks.\n"
                "    ↳ Please install it with: `pip install ipytest`"
            )

    # noinspection PyProtectedMember
    @staticmethod
    def cleanup_ipytest_env():
        import ipytest

        if getattr(ipytest._impl.random_module_path, "_filename", None):
            if Path(ipytest._impl.random_module_path._filename).exists():  # pyright: ignore [reportFunctionMemberAccess]
                Path(ipytest._impl.random_module_path._filename).unlink()  # pyright: ignore [reportFunctionMemberAccess]
                del ipytest._impl.random_module_path._filename  # pyright: ignore [reportFunctionMemberAccess]

            ipytest.clean()

    @cell_magic
    def ipytest_evals(self, line, cell):
        """
        Execute pytest evaluations in the current IPython cell.

        Usage:
            %%pytest_evals [optional arguments]
            def test_something():
                assert True
        """
        # Force reload to ensure fresh test environment
        from pytest_harvest import FIXTURE_STORE
        from IPython.core.getipython import get_ipython
        import ipytest

        FIXTURE_STORE.clear()

        run_args = shlex.split(line)

        if "--run-eval" not in run_args and "--run-eval-analysis" not in run_args:
            run_args.append("--run-eval")
            run_args.append("--run-eval-analysis")

        self.cleanup_ipytest_env()

        try:
            get_ipython().run_cell(cell)  # pyright: ignore [reportOptionalMemberAccess]

        except TypeError as e:
            if "raw_cell" in str(e):
                raise RuntimeError(
                    "The ipytest magic cannot evaluate the cell. Most likely you "
                    "are running a modified ipython version. Consider using "
                    "`ipytest.run` and `ipytest.clean` directly.",
                ) from e

            raise e

        try:
            ipytest.run(*run_args)
        except KeyboardInterrupt:
            self.cleanup_ipytest_env()
            raise


def load_ipython_extension(ipython):
    """
    Register the magic when the extension loads.
    """
    ipython.register_magics(EvalsMagics)
