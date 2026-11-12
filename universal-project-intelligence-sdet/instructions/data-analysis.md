# Data and persistence analysis

Identify database engines and evidence, schemas, tables/collections, entities, relationships, repositories/DAOs, migrations, query layers, transaction boundaries, caches, queues and object storage.

Document:
- data ownership by service/module;
- entity relationships and cardinality only when supported;
- keys, constraints and indexes when visible;
- schema evolution and migration ordering;
- data lifecycle and retention only when documented;
- validation, consistency and transaction handling;
- test data fixtures/factories and cleanup strategy.

Generate ERDs only when evidence is sufficient. Do not infer production schema from a partial ORM model. Never print real customer data, secrets, or sensitive row values.
