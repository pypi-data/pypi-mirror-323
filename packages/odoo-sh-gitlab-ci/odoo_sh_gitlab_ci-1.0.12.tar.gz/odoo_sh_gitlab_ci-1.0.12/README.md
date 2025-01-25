
# odoo-sh-gitlab-ci

This package simplifies and automates the process of updating Odoo.sh branches by interacting with a GitLab repository while using a GitHub repository as a container for multiple repositories. It ensures seamless management of submodules and branch synchronization, making the deployment process more efficient and maintainable.

## Installation

Install the package using pip:

```bash
pip install odoo-sh-gitlab-ci
```

## Usage

The package provides a command-line tool `odoo_sh_deploy` that can be used in two modes:

- **Initialization Mode (`--initialize`)**: Prepares the environment by configuring the SSH agent, adding SSH keys, and setting up Git configurations.
- **Deployment Mode**: Performs the actual deployment to Odoo.sh.

### Setting Up `variables.sh`

To simplify the configuration of environment variables, you can create a file called `variables.sh` in the root of your repository. Define your variables in this file using the following format:

```bash
export PRIVATE_DEPLOY_KEY="your_private_ssh_key"
export GITHUB_REPO="git@github.com:youruser/yourrepo.git"
export GITHUB_REPO_NAME="yourrepo"
export VERSION="18.0"
```

#### Example `variables.sh`

```bash
export PRIVATE_DEPLOY_KEY="-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA1o9qX..."
export GITHUB_REPO="git@github.com:youruser/yourrepo.git"
export GITHUB_REPO_NAME="yourrepo"
export VERSION="18.0"
```

**Important:** For security reasons, it is recommended to define `PRIVATE_DEPLOY_KEY` as a protected variable in GitLab CI/CD settings instead of hardcoding it in the `variables.sh` file.

### GitLab CI Configuration

To use `odoo-sh-gitlab-ci` in a GitLab CI pipeline, follow these steps:

1. **Add the `variables.sh` file to Your Repository**:
   Ensure the `variables.sh` file is located in the root of your repository.

2. **Update `.gitlab-ci.yml`**:
   Use the following configuration in your `.gitlab-ci.yml`:

   ```yaml
   odoo_sh_deploy:
     stage: pre
     tags:
       - odoo
     before_script:
       - 'command -v ssh-agent >/dev/null || ( apk add --update openssh )'
       - eval $(ssh-agent -s)
       - source variables.sh
       - pip install --root-user-action ignore odoo-sh-gitlab-ci
       - odoo_sh_deploy --initialize
     script:
       - source variables.sh
       - odoo_sh_deploy
   ```

   - **`before_script`**: This section installs the package and initializes the environment using the `--initialize` flag.
   - **`script`**: This section performs the deployment using `odoo_sh_deploy`.

3. **Example Pipeline Stages**:
   Here’s a full example of a pipeline that uses `odoo-sh-gitlab-ci`:

   ```yaml
   stages:
     - pre

   odoo_sh_deploy:
     stage: pre
     tags:
       - odoo
     before_script:
       - 'command -v ssh-agent >/dev/null || ( apk add --update openssh )'
       - eval $(ssh-agent -s)
       - source variables.sh
       - pip install --root-user-action ignore odoo-sh-gitlab-ci
       - odoo_sh_deploy --initialize
     script:
       - source variables.sh
       - odoo_sh_deploy
   ```

## License

This project is licensed under the AGPL-3.0 License.
