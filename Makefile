PYTHON := .venv/bin/python
MODEL := model/architecture.yml
VALIDATOR := tools/validate.py
PHYSICAL_GENERATOR := tools/generators/physical.py
DOMAIN_MODEL := model/domain.yml
DESIGN_MODEL := model/design.yml
WORKSPACE ?= ..
.PHONY: all check-env validate validate-domain validate_design validate-logical-expo validate-physical-expo validate-c4-expo validate-figuras classes physical physical-expo logical logical-expo c4 c4-expo figuras db dbml sql er dictionary sequences deployment traceability evidence clean

all: check-env validate physical physical-expo logical logical-expo c4 c4-expo db classes sequences deployment traceability figuras

check-env:
	@PYTHON="$(PYTHON)" bash tools/check_env.sh

validate:
	@echo "==> Validating architecture model"
	@$(PYTHON) $(VALIDATOR) $(MODEL) $(DOMAIN_MODEL)

validate-domain: validate
	@$(PYTHON) tools/domain_validation.py $(DOMAIN_MODEL) $(MODEL)

validate_design: validate
	@$(PYTHON) tools/validate_design.py $(DESIGN_MODEL) $(MODEL) $(DOMAIN_MODEL)

classes: validate_design
	@echo "==> Generating proposed class diagrams (PlantUML)"
	@$(PYTHON) tools/generators/classes.py $(DESIGN_MODEL) $(MODEL) $(DOMAIN_MODEL)

db: dictionary

dbml: validate-domain
	@$(PYTHON) tools/generators/to_dbml.py

sql: dbml
	@$(PYTHON) tools/generators/to_sql.py

er: sql
	@$(PYTHON) tools/generators/to_er_d2.py

dictionary: er
	@$(PYTHON) tools/generators/to_dictionary.py

physical: validate
	@echo "==> Generating physical views"
	@$(PYTHON) tools/run_legacy_views.py $(PHYSICAL_GENERATOR)

validate-physical-expo: validate
	@$(PYTHON) tools/generators/physical_presentation.py --validate-only

physical-expo: validate-physical-expo
	@echo "==> Generating physical presentation views (Graphviz)"
	@$(PYTHON) tools/generators/physical_presentation.py

logical: validate
	@echo "==> Generating logical architecture (D2 + ELK)"
	@$(PYTHON) tools/run_legacy_views.py tools/generators/logical.py

validate-logical-expo: validate
	@$(PYTHON) tools/generators/logical_presentation.py --validate-only

logical-expo: validate-logical-expo
	@echo "==> Generating logical presentation views (Graphviz)"
	@$(PYTHON) tools/generators/logical_presentation.py

c4: validate
	@echo "==> Generating C4 architecture"
	@$(PYTHON) tools/generators/c4.py

validate-c4-expo: validate
	@$(PYTHON) tools/generators/c4_container_presentation.py --validate-only

c4-expo: validate-c4-expo
	@echo "==> Generating slide-sized C4 container views"
	@$(PYTHON) tools/generators/c4_container_presentation.py

validate-figuras: validate
	@$(PYTHON) tools/generators/figuras.py --validate-only

# Document figures (out/figuras/): one PNG per page at 300 ppp, APA README per folder.
figuras: validate-figuras
	@echo "==> Generating document figures for Word (Graphviz + PlantUML)"
	@$(PYTHON) tools/generators/figuras.py

sequences: validate
	@echo "==> Generating sequence diagrams (PlantUML)"
	@$(PYTHON) tools/generators/sequences.py

deployment: validate
	@echo "==> Generating deployment diagrams (Graphviz)"
	@$(PYTHON) tools/generators/deployment.py

traceability: validate
	@echo "==> Generating the diagram traceability matrix"
	@$(PYTHON) tools/generators/traceability.py

# Optional: needs the sibling clones at the pinned revisions (WORKSPACE=<dir that holds them>).
evidence:
	@$(PYTHON) tools/generators/evidence.py --workspace $(WORKSPACE)

clean:
	@echo "==> Cleaning generated artifacts"
	@find build out -mindepth 1 -type f -delete 2>/dev/null || true
	@find build out -mindepth 1 -type d -empty -delete 2>/dev/null || true

.PHONY: test verify-artifacts test-postgres
test:
	@$(PYTHON) -m unittest discover -s tests -v

verify-artifacts:
	@$(PYTHON) tools/verify_artifacts.py

test-postgres: sql
	@$(PYTHON) tools/test_postgres.py
