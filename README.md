# OrgLang rationale

OrgLang separates the description of work from the agreements and communication mechanisms that make that work possible.

Imagine an online store that has received an order. The order must be packed and handed to a delivery service. Describing the steps is not enough: the store also needs to find a partner that can deliver the parcel and agree on the conditions of cooperation. If that partner needs a subcontractor, the same question appears again.

This illustrates two related but distinct concerns:

- **Processes** describe how work is organized and how participants interact while carrying it out.
- **Pools and transactions** describe which capabilities participants make available to one another and the agreements under which they can cooperate.

The distinction matters: a request to perform work does not itself mean that a suitable participant has been found, and an agreement to cooperate does not itself mean that the work is already being performed.

## The models

- [Executions and connections](about-executions-and-connections/README.md) describes the abstract runtime mechanisms: Computation aggregates, Execution roots, identifiers, placeholders, channels, publication, subscription, matching, and continuations.
- [Pools and transaction types](about-pools-and-transaction-types/README.md) describes pools, transaction protocols, negotiation, and established agreements.
- [Processes and session types](about-processes-and-session-types/README.md) describes process declarations, process expressions, and the protocols governing process communication.
- [Calls and spawns](about-calls-and-spawns/README.md) describes named-process invocation, Computation aggregate creation, channel transfer, and the boundary with pool-level spawning.
- [Glossary](GLOSSARY.md) collects shared terminology.

The abstract mechanisms are deliberately separated from the models built on top of them. The pool and process specifications define their own domain-specific rules without turning those rules into assumptions of the general computation-and-channel model.
