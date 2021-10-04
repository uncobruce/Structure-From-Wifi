# Structure from WiFi (SfM)
A novel algorithm for geometrically mapping an environment using WiFi. This is a work in progress. 

## Organization
* k_visibility: contains programs for implementing the k-visibility algorithm.
   * `k_visibility.py`: Implementation of the paper [A Hybrid Metaheuristic Strategy for Covering with Wireless Devices](http://www.jucs.org/jucs_18_14/a_hybrid_metaheuristic_strategy/jucs_18_14_1906_1932_bajuelos.pdf)  (2012). Constructs k-visibility regions of a given map.
   * `k_visibility_floorplan.py`: Implementing k-visibility algorithm, but for floorplans that tend to have a "double wall" effect. Floorplans were taken from the [HouseExpo](https://github.com/TeaganLi/HouseExpo) indoor floorplan dataset.
   * `vertices2.py`: needed for k_visibility_floorplan.py. Identifies the vertices of a given floorplan image as well as the contour coordinates of the environment.
   
* inverse_k_visibility: novel algorithm which is used to obtain a map of the environment. This was is tested by simulation and experimentally.
  * full_inverse: solves the problem when given a full k-visibility colour-map to obtain the 2D map. 
  * sparse_inverse: solves the problem when given sparse k-value inputs to obtain a partial map. 
