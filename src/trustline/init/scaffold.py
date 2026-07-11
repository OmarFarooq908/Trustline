"""Scaffold a Trustline workspace from bundled presets."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from trustline.exceptions import TrustlineError
from trustline.templates.presets import PRESETS, InitPreset, templates_dir
from trustline.templates.render import DEFAULT_INIT_VARS, render_template


@dataclass(frozen=True)
class InitResult:
    """Paths written by ``run_init``."""

    output_dir: Path
    contracts_dir: Path
    profiles_path: Path
    audit_profile_path: Path | None


def _slugify(product: str) -> str:
    slug = product.strip().lower().replace(" ", "_").replace("-", "_")
    return "".join(ch for ch in slug if ch.isalnum() or ch == "_") or "my_product"


def build_init_variables(
    *,
    product: str,
    owner: str,
    cutover_date: str | None = None,
) -> dict[str, str]:
    """Build placeholder values for template rendering."""
    variables = dict(DEFAULT_INIT_VARS)
    variables["product_name"] = product
    variables["product_slug"] = _slugify(product)
    variables["owner_email"] = owner
    if cutover_date is not None:
        variables["cutover_date"] = cutover_date
    return variables


def _write_rendered(path: Path, source: Path, variables: dict[str, str]) -> None:
    raw = source.read_text(encoding="utf-8")
    path.write_text(render_template(raw, variables), encoding="utf-8")


def _generated_readme(preset: InitPreset, output_dir: Path) -> str:
    return f"""# Trustline workspace

Preset: **{preset.name}** — {preset.description}

Pattern reference: {preset.pattern_doc}

## Next steps

```bash
trustline validate --contracts {output_dir}/contracts
trustline audit --contracts {output_dir}/contracts --profiles {output_dir}/profiles.yml
```

Edit `{{ ref('table_name') }}` placeholders in contract YAML to match your warehouse tables.
Set `duckdb_path` in `profiles.yml` before running an audit against your database.
"""


def run_init(
    preset_name: str,
    output_dir: Path,
    *,
    variables: dict[str, str],
    force: bool = False,
) -> InitResult:
    """Copy and render preset templates into ``output_dir``."""
    if preset_name not in PRESETS:
        available = ", ".join(sorted(PRESETS))
        msg = f"unknown preset {preset_name!r}; choose one of: {available}"
        raise TrustlineError(msg)

    preset = PRESETS[preset_name]
    template_root = templates_dir()

    if output_dir.exists():
        if not force:
            msg = (
                f"{output_dir} already exists. Use --force to overwrite generated files, "
                "or --output-dir PATH for a different location."
            )
            raise TrustlineError(msg)
    else:
        output_dir.mkdir(parents=True)

    contracts_dir = output_dir / "contracts"
    contracts_dir.mkdir(parents=True, exist_ok=True)

    for filename in preset.contract_files:
        source = template_root / filename
        dest = contracts_dir / filename
        _write_rendered(dest, source, variables)

    audit_profile_path: Path | None = None
    if preset.include_audit_profile:
        audit_profile_path = output_dir / "audit_profile.yaml"
        _write_rendered(
            audit_profile_path,
            template_root / "audit_profile_ml_crm.yaml",
            variables,
        )

    profiles_path = output_dir / "profiles.yml"
    profiles_template = template_root / "profiles.yml.template"
    if force or not profiles_path.exists():
        shutil.copyfile(profiles_template, profiles_path)

    readme_path = output_dir / "README.md"
    if force or not readme_path.exists():
        readme_path.write_text(_generated_readme(preset, output_dir), encoding="utf-8")

    return InitResult(
        output_dir=output_dir,
        contracts_dir=contracts_dir,
        profiles_path=profiles_path,
        audit_profile_path=audit_profile_path,
    )
