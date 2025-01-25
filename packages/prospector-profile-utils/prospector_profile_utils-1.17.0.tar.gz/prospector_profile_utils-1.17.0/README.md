# Prospector profile utils

It contains some utility Prospector profiles.

## Usage

```bash
pip install prospector-profile-utils
```

Then, in your `.prospector.yaml` file, you can use the profiles like this:

```yaml
inherits:
  - utils:base
  - utils:c2cwsgiutils
  - utils:no-design-checks
```

It provide also an alternate base witch activate less strict checks:

```yaml
inherits:
  - utils:base-less-strict
```

Other profiles:

- `utils:fix`: Disable some not well working riles.
- `utils:autofix`: Activate the auto fix options.
- `utils:unsafe`: Activate the unsafe fix options.

## Contributing

Install the pre-commit hooks:

```bash
pip install pre-commit
pre-commit install --allow-missing-config
```
