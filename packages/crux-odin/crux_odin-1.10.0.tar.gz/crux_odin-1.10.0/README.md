![Odin logo](https://github.com/cruxinformatics/crux-python/blob/master/crux-odin-logo.png?raw=true)

# Crux-Odin Library
**Open Data Integration Nomenclature** (ODIN) is Crux’s standard for declarative 
data delivery. ODIN provides a nomenclature for delivery that incentivizes 
industry-standard GitOps practices. ODIN specs are inherently abstracted from 
their underlying control planes and workflow frameworks, but work with the 
Crux External Data Platform.

# Development
This project depends on pyenv for python version management and Poetry for package management and configuration. For instruction on local machine setup please refer to the below resources:

[Pyenv Install](https://github.com/pyenv/pyenv#installation)
[Poetry Install](https://python-poetry.org/docs/#installation)


# Usage

Right now we store `crux-odin` in the [Google Artifact Registry](https://console.cloud.google.com/artifacts/python/crux-ci/us/crux-python/crux-odin?project=crux-ci).
This will be changed when we promote to Pypi. For now, make sure you have a file called `~/.pypirc` in your
home directory with the following content:

```ini
[distutils]
index-servers = crux-python

[crux-python]
repository: https://us-python.pkg.dev/crux-ci/crux-python/
```

To install with the various tools:

#### pipenv
Add the following section to your `Pipfile`:
```ini
[[source]]
name = "google"
url = "https://us-python.pkg.dev/crux-ci/crux-python/simple"
verify_ssl = true

[pipenv]
disable_pip_input = false
```
and add 
```
keyring = "*"
"keyrings.google-artifactregistry-auth" = "*"
crux-odin = "*"
```
under the `[packages]` section. Then do a `pipenv sync --dev`.

#### pip
```bash
pip install crux-odin==1.5.7 --index-url https://us-python.pkg.dev/crux-ci/crux-python/simple
```

#### poetry
Set up the poetry authentication with
```bash
poetry config http-basic.google oauth2accesstoken $(gcloud auth print-access-token)
```
Add a `gcp` entry to your `pyproject.toml`:
```bash
poetry source add --priority=supplemental gcp https://us-python.pkg.dev/crux-ci/crux-python/simple/
```
and also add the `crux-odin` dependency with
```
poetry add crux-odin=1.5.7 --source=gcp 
```
to edit the `pyproject.toml`. Then do a `poetry install`.

For all installation methods, you can always uninstall `crux-odin` with `pip uninstall crux-odin`.

#### Changing Your Code

```python
from crux_odin.dict_utils import yaml_file_to_dict
from crux_odin.dataclass import create_workflow

workflow = create_workflow(yaml_file_to_dict("file.yaml"))  # Version of Workflow gotten from YAML file
```

#### Validating YAML
```python
from crux_odin.validate_yaml import validate_yaml

validate_yaml('file.yaml')
```

# Manage Versions
To update a version
1. create a branch
```bash
git checkout -b release/[VERSION]
```

2. bump version
```bash
poe version_check # shows output without bumping version
poe version_bump # to bump version default
poe version_bump_patch # to increment patch version
poe version_bump_minor # to increment minor version
poe version_bump_major # to increment major version
```

3. create PR and merge in main branch
4. push git tag
```bash
git push origin [VERSION]
```

Reference: https://commitizen-tools.github.io/commitizen/commands/bump/

# Supported Versions

See [this page](https://cruxinformatics.atlassian.net/wiki/spaces/TECH/pages/773685252/Description+of+Odin+YAML+fields) 
for a description of the YAML fields.

## V1.0.0 - Crux's proprietary PDK framework

### Supported information:

* ID (airflow specific)
* Connection info + extraction info
* Normalizer spec
* Schema history + schema validations
* Context / Environment Variables

```yaml
id: sample_id
run_uber_step: true

global:
  global:
    encoding: ascii
    timedelta:
      days: -1
    schema_def:
      na_values: [ "", " " ]
    crux_api_conf: ${SAMPLE_ID_API}
    endpoint: ${API_HOST}
  extract:
    action_class: pipeline.crux_pdk.actions.extract.extractor.ShortCircuitExtractor
    connection_lib: pipeline.custom_libs.sample.connector
    fetch_method: fetch_directory
    remote_path: /pub/sparx/
    connection:
      type: SAMPLE_ID_CONNECTOR
      conf: ${CRUX_SPARTA_SFTP}
      zendesk_conf:
        wait_time: 60
        payload:
          organization_id: 123123123123
          role: end-user
          ticket_restriction: organization
          skip_verify_email: true

pipelines:
  - id: sample_id
    global:
      global:
        supplier_implied_date_regex: active_users_(?P<YYYY>\d{4})(?P<MM>\d{2})(?P<DD>\d{2})
        provenance_file_patterns:
          origin_patterns:
            - active_ts_users_(?P<YYYY>\d{4})(?P<MM>\d{2})(?P<DD>\d{2})
          return_patterns:
            - active_ts_users_(?P<YYYY>\d{4})(?P<MM>\d{2})(?P<DD>\d{2})
    steps:
      - id: extract
        category: short_circuit
        conf:
          file_patterns:
            - active_users_{FD_YYYY}{FD_MM}{FD_DD}\.csv
```
Note: the outside global is inherited by the pipelines, the 'inside' global is inherited by the steps.
The IDs have to match, `extract` above matches `- id: extract`

## V1.1.0 - True Declarative Dataset
This is the first version of the spec that replaces the .py DAG files with full declarative syntax in YAML.

**Newly supported capabilities**

* Schedule
```yaml
...:
  dag:
   dag_catchup: false            # (schedule catch up runs to current date starting from start date)
   dag_start_date: '2023-03-12'  # (when the dag start running)
   enable_delivery_cache: false  # (required for dag files)
   max_active_runs: 10.          # (max active run in airflow system for this dag)
   owner: CruxInformatics        # (owner of the dag)
   priority_weight: 1            # (the order in which this dag is given priority compared to others)
   schedule_interval: '@once'    # (dag schedule, when dag will be triggered after dag start date)
   queue: kubernetes             # (the worker pool to run the jobs, 
                                 # on cloud composer options: default and kubernetes, AF 1.9: default, ongoing and history)
   tags:                         # (enable the tag searches/filtering on optional and only available in cloud composer)
   - spm
   - delivery-dispatch
```

## V1.2.0 - Dataset, Data Product, and Organization Identifiers
Version 1.2 brings Dataset ID, a grouping of all data delivered or failed together, Data Product ID, a catalog-oriented collection of Datasets, and Org ID, a useful organizational grouping of Datasets. These fields are opinionated to Crux's control plane, but we find these concepts are widely used and necessary for most Control Plane implementations of ODIN. We will be reviewing generic versions of this in the future. The `dataset_id` and `data_product_id` will be validated to make sure they are in the `org_id`. `crux_api_conf` _is not_ deprecated in this version (yet).
`data_product_id` is optional while `dataset_id` and `org_id` are required.

**Newly supported capabilities**
* Dataset ID
* Data Product ID
* Org ID
```yaml
...:
  metadata:
      dataset_id: 'Ds012345'          # a grouping of transactional data. 1:1 with ODIN spec
      data_product_id: 'Dp012345'     # a collection of Datasets for cataloging and productization
      org_id: 'Or012345'              # organizational identifier for a control plane
```

## V1.3.0 - Vendor Declarations, Declared & Observed Schemas
Version 1.3 adds support for users to track schemas that are declared in vendor documentation, as well as observed from profiling the data. These schemas are only advisory, as the configured schema is what is primarily used in  control plane implementations. These new fields are made optional, and the vendor-declared schema is defined and validated according to the requirements needed for ODIN to support hydration of the Crux Catalog. Frame description is also added as an optional field to the configured schema. 

**Newly supported capabilities**
* declared_schema_def
* observed_schema_def
* vendor_doc
* frame_description

```yaml
...:
pipelines:
  - id:                           
    vendor_doc:                   # URI (optional)
    global:
      global:
          schema_def:                   # Already exists
            ...
          declared_schema_def:          # declared or curated schema (optional)
            vendor_table_name:
            vendor_table_description:
            vendor_schedule:
            fields:
            - name:
              data_type:
              configured_data_type:   # must exist in schema_def and have same type
              configured_name:        # must exist in schema_def and have same name
              column_number:
              is_primary_key:
              page_number:
              vendor_description:
            - name: ...
          observed_schema_def:          # observed from profiling the data
            fields:
            - data_type:
              name:
              configured_data_type:   # must exist in schema_def and have same type
              configured_name:        # must exist in schema_def and have same name
            - name: ...
```

## V1.4.0 Availability Deadlines
Allows the Control Plane the ability to apply to hydrate delivery deadlines. This provides users visibility into upstream data availability issues by specifying a cadence for expected new data.

**Newly supported capabilities**
* Deadline
```yaml
availability_deadlines:
- deadline_minute: '30' # The minute to run the check
  deadline_hour: '8' # The hour to evaluate the 
  deadline_day_of_month: '*' # Used for monthly and longer frequencies
  deadline_month: '*' # Used for yearly frequency
  deadline_day_of_week: '1' # supports cron pattern day range and *W (for weekdays)
  deadline_year: '*' # Must be *
  file_frequency: 'weekly' # One of "intraday", "daily", "weekly", "bi-weekly", "monthly", "semi-annual", "yearly"
  timezone: 'UTC'
- deadline_minute: '30' # Supports multiple deadlines 
  deadline_hour: '8'
  deadline_day_of_month: '*'
  deadline_month: '*'
  deadline_day_of_week: '5'
  deadline_year: '*'
  file_frequency: 'weekly'
  timezone: 'UTC'
piplines:
...
```

## V1.5.0 - Destinations
This allows a list of Destinations selected from the domain model to be used by Delivery Dispatch.

**Newly supported capabilities**
* Destinations
```yaml
destinations:
  - id: AQxxxxxxxxxx
    name: Customer FTP site
...
```

## V1.6.0 - Require crux_api_conf at the OUTER level
We used to allow the `crux_api_conf` declaration to exist at the `step` level or
under the `conf` keyword of any step. If it was declared there, then we would move
it up to the global level when we read in the YAML and created a `Workflow` object
(we'd select the first one we found). We now longer do this and require that the
`crux_api_conf` exist at the outer level of the YAML file.

**Example**
```yaml
id: sample_id
...
crux_api_conf: ${SAMPLE_ID_API}
```

# Roadmap
This roadmap outlines the incremental modeling capabilities that we plan to support in ODIN, but is not a commitment.

## V1.X.0 Notifications
This allows for notification channels.
