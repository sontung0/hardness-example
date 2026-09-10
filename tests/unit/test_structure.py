"""Structural / architectural tests — AR-1, AR-2, AR-5.

Automated verification of architectural invariants that were previously
checked only by manual code review.  Running these turns PARTIAL status
into PASS in the traceability gate.
"""

import ast
import importlib
import inspect
import os

import pytest

SRC_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "src")

# ── AR-2: Structural seed — 6 source files must exist ──────────────────────

REQUIRED_SOURCE_FILES = [
    "main.py",
    "routes.py",
    "services.py",
    "store.py",
    "models.py",
    "auth.py",
]


class TestAR2SeedFiles:
    """AR-2 (P1): The project must ship exactly these 6 source modules."""

    @pytest.mark.structural
    @pytest.mark.parametrize("filename", REQUIRED_SOURCE_FILES, ids=REQUIRED_SOURCE_FILES)
    def test_source_file_exists(self, filename: str) -> None:
        path = os.path.join(SRC_DIR, filename)
        assert os.path.isfile(path), f"Required source file missing: {filename}"

    @pytest.mark.structural
    def test_no_unexpected_source_files(self) -> None:
        """No extra .py files beyond the seed set (ignores __init__.py)."""
        actual = {
            f for f in os.listdir(SRC_DIR) if f.endswith(".py") and f != "__init__.py"
        }
        expected = set(REQUIRED_SOURCE_FILES)
        unexpected = actual - expected
        assert not unexpected, f"Unexpected source files: {unexpected}"


# ── AR-1: Layered architecture (Routes → Services → Store) ──────────────────

class TestAR1LayeredArchitecture:
    """AR-1 (P1): Import dependency chain must be unidirectional.

    The allowed dependency edges are:
        routes  →  services, auth, models
        services → store, (bcrypt stdlib only)
        auth     → (jwt stdlib only)
        store    → (no internal imports)

    Forbidden: store importing services, services importing routes, etc.
    """

    @staticmethod
    def _get_imports(module_name: str) -> set[str]:
        """Return the set of top-level names imported by a module."""
        mod = importlib.import_module(module_name)
        source = inspect.getsource(mod)
        tree = compile(source, f"{module_name}.py", "exec", ast.PyCF_ONLY_AST)  # type: ignore[name-defined]
        # Lightweight: just scan lines for 'import X' / 'from X import'
        imports = set()
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        return imports

    @pytest.mark.structural
    def test_store_has_no_internal_imports(self) -> None:
        """AR-1: store.py must not import any sibling project modules."""
        imports = self._get_imports("store")
        internal = {"routes", "services", "auth", "models", "main"}
        violations = imports & internal
        assert not violations, f"store.py imports internal modules: {violations}"

    @pytest.mark.structural
    def test_services_depends_on_store(self) -> None:
        """AR-1: services.py must import from store (downward dependency)."""
        imports = self._get_imports("services")
        assert "store" in imports, "services.py should import from store"

    @pytest.mark.structural
    def test_services_does_not_import_routes(self) -> None:
        """AR-1: services.py must NOT import routes (no upward dependency)."""
        imports = self._get_imports("services")
        assert "routes" not in imports, "services.py must not import routes"

    @pytest.mark.structural
    def test_routes_depends_on_services(self) -> None:
        """AR-1: routes.py must import from services (downward dependency)."""
        imports = self._get_imports("routes")
        assert "services" in imports, "routes.py should import from services"

    @pytest.mark.structural
    def test_routes_does_not_import_store(self) -> None:
        """AR-1: routes.py must NOT import store directly (must go through services)."""
        imports = self._get_imports("routes")
        assert "store" not in imports, "routes.py must not import store directly"

    @pytest.mark.structural
    def test_routes_imports_auth(self) -> None:
        """AR-1: routes.py uses auth dependency for JWT validation."""
        imports = self._get_imports("routes")
        assert "auth" in imports, "routes.py should import from auth"


# ── AR-5: Store lifecycle (module-level dict) ────────────────────────────────

class TestAR5StoreLifecycle:
    """AR-5 (P1): The store must use a module-level dict that can be
    cleared between tests (in-memory lifecycle)."""

    @pytest.mark.structural
    def test_users_is_module_level_dict(self) -> None:
        """AR-5: store.users must be a plain dict at module level."""
        import store

        assert hasattr(store, "users"), "store module must have 'users' attribute"
        assert isinstance(store.users, dict), "store.users must be a dict"

    @pytest.mark.structural
    def test_store_clearable(self) -> None:
        """AR-5: store.users.clear() must work (enables test isolation)."""
        import store

        store.add_user("temp_user", "hash123", "Temp")
        assert "temp_user" in store.users

        store.users.clear()
        assert len(store.users) == 0, "store.users.clear() must empty the dict"

    @pytest.mark.structural
    def test_store_persistence_across_imports(self) -> None:
        """AR-5: Multiple imports of 'store' share the same dict instance."""
        import store as s1
        import store as s2

        assert s1.users is s2.users, "store.users must be the same object across imports"
