# Structure from WiFi (SfM)
A method for geometrically mapping an environment using WiFi, based on a novel "inverse k-visibility" algorithm which uses trajectory information and RSSI data to obtain a map of the environment. This is a work in progress. 

## Organization
* full_inverse: solves the inverse k-visibility problem when given a full k-visibility colour-map input to obtain a 2D map.
* sparse_inverse: solves the inverse k-visibility problem when given sparse k-value inputs to obtain a partial map. 
  * Inputs:
    * floorplans: 2D typical indoor floorplans, taken from the [HouseExpo](https://github.com/TeaganLi/HouseExpo) indoor floorplan dataset.
    * random_trajectories: manually drawn trajectories used for the simulation.
  * data_processing: processing raw data to obtain a trajectory object with associated k-values and router point.
    * ```drawcontours.py```: draw contours for the indoor floorplan input.
    * ```kvisibility_algorithm.py```:  Implementation of the paper [A Hybrid Metaheuristic Strategy for Covering with Wireless Devices](http://www.jucs.org/jucs_18_14/a_hybrid_metaheuristic_strategy/jucs_18_14_1906_1932_bajuelos.pdf)  (2012). Constructs k-visibility regions of a given floorplan, and compensates for the "double-wall" effect that occurs in floorplan contours.
    * ```associate_traj_kvals.py```: return a trajectory object which associates trajectory coordinates with corresponding k-values at every point, and contains router point information.
   * geometric analysis 
     * ```sparse_inverse_coneshapes.py```: algorithm which uses cone shapes to return refined k-value polygons based on trajectory and associated k-values
   * grid_mapping 
     * ```grid_map.py```: plot gridmap with trajectory, apply probabilistic model to estimate wall locations in grid map
    * ```main.py```: for running main program 

   
* inverse_k_visibility: novel algorithm which is used to obtain a map of the environment. This is tested by simulation and experimentally.
  * full_inverse: solves the problem when given a full k-visibility colour-map to obtain the 2D map. 
  * sparse_inverse: solves the problem when given sparse k-value inputs to obtain a partial map. 
