"""Tests for init template placeholder rendering."""

from __future__ import annotations

from trustline.templates.render import DEFAULT_INIT_VARS, render_template


def test_render_preserves_ref_syntax() -> None:
    """dbt-style ref() placeholders must survive rendering."""
    text = "SELECT * FROM {{ ref('donor_gifts') }} WHERE id = {{ product_slug }}"
    rendered = render_template(text, {"product_slug": "acme"})
    assert "{{ ref('donor_gifts') }}" in rendered
    assert "acme" in rendered
    assert "{{ product_slug }}" not in rendered


def test_render_leaves_unknown_placeholders_unchanged() -> None:
    """Unknown keys should not be substituted."""
    text = "owner: {{ owner_email }}, extra: {{ unknown_key }}"
    rendered = render_template(text, {"owner_email": "team@example.com"})
    assert "team@example.com" in rendered
    assert "{{ unknown_key }}" in rendered


def test_render_substitutes_default_init_vars() -> None:
    """Default init variables should replace product and date placeholders."""
    text = (
        "product: {{ product_name }}\n"
        "slug: {{ product_slug }}\n"
        "window: {{ observation_start }} to {{ observation_end }}"
    )
    rendered = render_template(text, DEFAULT_INIT_VARS)
    assert "product: my_product" in rendered
    assert "slug: my_product" in rendered
    assert "window: 2025-01-01 to 2025-03-31" in rendered


def test_render_custom_slug_and_dates() -> None:
    """Callers can override slug and date placeholders."""
    variables = {
        **DEFAULT_INIT_VARS,
        "product_slug": "acme_propensity",
        "cutover_date": "2025-06-01",
    }
    text = "slug: {{ product_slug }}, cutover: {{ cutover_date }}"
    rendered = render_template(text, variables)
    assert "slug: acme_propensity" in rendered
    assert "cutover: 2025-06-01" in rendered
