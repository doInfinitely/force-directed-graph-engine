An alternative model of classical electricity and magnetism that I developed
in order to compute force directed graphs efficently. Does not rely on
interaction at a distance between charged moieties, instead forces are mediated
by collisions between charged or massive (as in, "having mass") particles and
force carriers, that are emitted periodically by particles. In effect, this
reduces electromagnetism to collision checking. One can produce behavior that
mimics the classical field-based formulation perfectly at the limit where the
frequency of emission and the speed of the force carriers approaches infinity.
Finite values produce an approximation of the classical system. Since this 
reformulation reduces E&M to collision checking, many optimizations/shortcuts
are possible, for instance, charge carriers can be discarded once it's no
longer possible for the carrier to interact with any particle. Another example
is that the space can be decomposed into disjoint subspaces and the physics in
each subspace run in parallel, the disjoint subspaces only communicating when
an object from one subspace impinges on another subspace.

Interestingly, in this formulation, the photon is a doppler effect of an
oscillating charged particle.
