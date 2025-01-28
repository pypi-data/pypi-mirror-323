# Basic Usage

````{important}
If you only installed the core package, the following example will raise import errors from missing dependencies. 
To use the {class}`~cohesivm.devices.agilent.Agilent4156C`, {class}`~cohesivm.interfaces.ma8x8.MA8X8`, and 
{class}`~cohesivm.devices.ossila.OssilaX200` classes, you need to install the ``agilent``, ``ma8x8``, and ``ossila`` 
extras, respectively. To add all dependencies at once, install the ``full`` extra with this command:
```console
pip install cohesivm[full]
```
````

With working implementations of the main components ({class}`~cohesivm.devices.Device`,
{class}`~cohesivm.interfaces.Interface`, {class}`~cohesivm.measurements.Measurement`), setting up and running an
experiment only takes a few lines of code:

```python
from cohesivm import config
from cohesivm.database import Database, Dimensions
from cohesivm.experiment import Experiment
from cohesivm.progressbar import ProgressBar
from cohesivm.devices.agilent import Agilent4156C
from cohesivm.interfaces import MA8X8
from cohesivm.measurements.iv import CurrentVoltageCharacteristic

# Create a new or load an existing database
db = Database('Test.h5')

# Configure the components
smu = Agilent4156C.SweepVoltageSMUChannel()
device = Agilent4156C.Agilent4156C(channels=[smu], **config.get_section('Agilent4156C'))
interface = MA8X8(com_port=config.get_option('MA8X8', 'com_port'), pixel_dimensions=Dimensions.Circle(radius=0.425))
measurement = CurrentVoltageCharacteristic(start_voltage=-2.0, end_voltage=2.0, voltage_step=0.01, illuminated=True)

# Combine the components in an experiment
experiment = Experiment(
    database=db,
    device=device,
    interface=interface,
    measurement=measurement,
    sample_id='test_sample_42',
    selected_contacts=None
)

# Optionally set up a progressbar
pbar = ProgressBar(experiment)

# Run the experiment
with pbar.show():
    experiment.quickstart()
```

If you want to change the measurement device to a different one, you only need to adjust the lines for the
{class}`~cohesivm.channels.Channel` and the {class}`~cohesivm.devices.Device` accordingly:

```python
from cohesivm.devices.ossila import OssilaX200
smu = OssilaX200.VoltageSMUChannel()
device = OssilaX200.OssilaX200(channels=[smu], **config.get_section('OssilaX200'))
```
