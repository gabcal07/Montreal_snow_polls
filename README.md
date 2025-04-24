# Operational Research Project: Snowplow & Drone Simulation

## Setting Up the Execution Environment

Before running the program, execute the following commands to install all required libraries:

```bash
python3 -m venv env

source env/bin/activate

pip install -r requirements.txt
```

## Running Snowplow or Drone Simulation

After installing the required libraries via `requirements.txt`, follow these steps to launch the project and begin snow removal simulation in Montreal:

1. Navigate to the source directory:
   ```bash
   cd src
   ```
2. Launch the project:
    ```bash
    python3 ero1.py
    ```
3. When finished:
    ```bash
    cd ..
    
    deactivate

    rm -rf env
    ```

## Selecting Scenarios and Neighborhoods

Once the program launches, select your desired scenarios and neighborhoods for snow removal simulation. After compilation completes, `.html` files will be generated in the chosen neighborhood's folder.

## Visualizing Operations

To visualize snowplow routes or drone paths, open the corresponding `.html` file in a web browser. Files follow this naming convention:

- For snowplows: `neighborhood-name_animation_{scenario_number}.html`
- For drones: `animation.html`

### Example

Open the file in a web browser using either:

```bash
firefox filename.html
```
Or simply drag-and-drop the file into your browser.

Click the animation button to view snow removal operations or drone flight paths in your selected neighborhood.

### Web Interface

Alternatively, use the React web interface located in the `ERO1` folder:

1. Navigate to the ERO1 directory:
   ```bash
   cd ERO1/
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Launch the development server:
   ```bash
   npm run dev
   ```

4. Click the link displayed in your terminal. The interface allows:
   - Selecting different neighborhoods and scenarios
   - Viewing drone-only flight paths

### Important Note

The Rivière-des-Prairies–Pointe-aux-Trembles neighborhood is particularly large, so data processing may take significant time. Please be patient while visualization files are generated.

# Project Structure: SNOW REMOVAL SIMULATION

Detailed description of main directories and files:

## Directories and Files

### Neighborhood Folders
Each Montreal neighborhood has its own folder containing:
- `animation.html`: Visualization of snow removal/drone paths
- `graph.pkl`: Serialized data file for complex data structures
- `map.html`: Interactive results map
- Additional HTML files for specific animations

### `AUTHORS`
Lists project creators and contributors.

### `ERO1`
Web development directory (Front-end):
- Framework configuration files (React, Vite, etc.)
- Public resources and React components

### `src`
Core source code:
- `drone.py`: Drone simulation script
- `ero1.py`: Main snow removal simulation script
- `SPRP.py`: Project-specific functions

### `test`
Unit and integration tests:
- `test_drone_min_cost.py`: Tests drone minimum-cost algorithms
- `test_drone.py`: Tests drone simulation functionality

### `utils`
Data and graph utilities:
- `create_graph.py`: Script for creating test graphs

## Root Files
- **README.md**: Detailed installation and usage instructions
- **requirements.txt**: Required Python libraries for script execution
