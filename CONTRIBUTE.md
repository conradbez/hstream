## Running installing and running locally in `.test-venv`

```bash
uv venv test-env && source test-env/bin/activate  # Create new uv environment and activate
pip install -e .  # Install local library in editable mode (simulates PyPI install)
hstream run your_test_script.py  # Test the library manually with a script
```




## Deploy

We use automatic versioning and deployment with hatch-vcs and GitHub Actions.

### How It Works:

```
Push to main → Tests pass → Auto-create tag → Build with version → Publish to PyPI → Create GitHub release
```

Every push to the main branch will:
1. Run all tests
2. Automatically create a new git tag (patch version bump: v0.1.58 → v0.1.59)
3. Build the package with the version from the tag
4. Publish to PyPI automatically
5. Create a GitHub release with changelog

### Important: Initial Setup Needed

Before the auto-versioning works, you need to create an initial tag:

```bash
# Switch to main branch and create initial tag
git checkout main
git tag v0.1.58  # Use the next version number
git push origin v0.1.58
```

After that, every push to main will auto-increment the patch version.

### Manual Version Bumps

The default is to bump the patch version (0.1.X), but you can control the version bump with commit messages:

- **Patch bump** (default): `git commit -m "fix: bug fix"`
- **Minor bump**: `git commit -m "feat: new feature"`
- **Major bump**: `git commit -m "feat!: breaking change"`

### Old Manual Process (Deprecated)

<details>
<summary>Click to see the old manual deployment process (no longer used)</summary>

1. increment version in `setup.py`
2. `rm -rf build/ hstream.egg-info/ dist/`
3. `pip install twine build`
4. `python -m build`
5. `twine upload dist/*`

</details>

## Kill orphaned uvicorn processes

`kill -9 $(lsof -t -i:8000)` (or whatever port they we're using)


# Precommit

`uv run pre-commit run --all-files`
