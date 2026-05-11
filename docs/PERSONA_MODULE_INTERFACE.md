# PersonaModule@1.0 Interface

Canonical persona module contract for MoJoAssistant.

## Provider Name
- `agency_persona`

## Contract
Implemented through `PersonaProvider` in core:
- `get_version() -> ProviderVersion`
- `generate(spec: PersonaSpec) -> role_definition`
- `score(role_def) -> PersonaScore`
- `list_personas(filter=None) -> PersonaSummary[]`

## Default Implementation
- `app.roles.persona_provider.AgencyPersonaModule`

## Module Descriptor
- `submodules/agency-agents/module.json`

## MCP Integration Paths
- `role(action="create", persona_spec=...)`
- `role(action="create", persona_file=...)`
- `role(action="persona_list", filter=...)`
- `role(action="persona_score", role=...|role_id=...)`

## Compatibility
- `contract_version`: `1.0`
- Keep return shapes stable for conformance tests.
