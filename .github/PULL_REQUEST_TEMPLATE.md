## Pull Request

### Description
Brief description of changes.

### Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update

### Component Modified
- [ ] `shunollo_core/` (Physics Engine)
- [ ] `shunollo_runtime/` (Transport Layer)
- [ ] `tests/`
- [ ] `docs/`
- [ ] `examples/`

### Schism Compliance Checklist
> **The Cardinal Rule**: Core must never import from external applications.

- [ ] No external application imports added to `shunollo_core/`
- [ ] No external application imports added to `shunollo_runtime/`
- [ ] No network calls added to `shunollo_core/`
- [ ] No `pickle`, `eval`, or `exec` usage

### CLA
- [ ] I have read and agree to the [Contributor License Agreement](.github/CLA.md)

### Testing
- [ ] I have added tests that prove my fix/feature works
- [ ] All new and existing tests pass (`pytest tests/`)

### Documentation
- [ ] I have updated relevant documentation
- [ ] I have added docstrings with physics mappings (if applicable)
