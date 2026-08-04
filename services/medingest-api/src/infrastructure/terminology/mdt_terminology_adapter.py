import logging
from typing import Any

from src.application.ports.iterminology_service import ITerminologyService
from src.domain.terminology.value_objects import TerminologyMapping, TerminologyMapResult

logger = logging.getLogger(__name__)

class MdtTerminologyAdapter(ITerminologyService):
    """Integrates Google Health MDT LoincQueryEngine and maps multi-coding systems."""

    _ANALYTE_DB: dict[str, dict[str, Any]] = {
        "glucose": {
            "loinc": [
                {"code": "15074-8", "display": "Glucose [Mass/volume] in Blood", "confidence": 0.99},
                {"code": "2339-0", "display": "Glucose [Mass/volume] in Blood - random", "confidence": 0.85}
            ],
            "snomed": "434912009",  # Blood glucose measurement
            "snomed_display": "Blood glucose measurement",
            "icd10": "E11.9",       # Type 2 diabetes mellitus
            "icd10_display": "Type 2 diabetes mellitus without complications",
            "rxnorm": None
        },
        "cholesterol": {
            "loinc": [
                {"code": "2093-3", "display": "Cholesterol [Mass/volume] in Serum or Plasma", "confidence": 0.99}
            ],
            "snomed": "121868005", # Serum cholesterol measurement
            "snomed_display": "Serum cholesterol measurement",
            "icd10": "E78.0",      # Pure hypercholesterolemia
            "icd10_display": "Pure hypercholesterolemia",
            "rxnorm": None
        },
        "hemoglobin": {
            "loinc": [
                {"code": "718-7", "display": "Hemoglobin [Mass/volume] in Whole blood", "confidence": 0.99}
            ],
            "snomed": "365615001",  # Hemoglobin measurement
            "snomed_display": "Hemoglobin measurement",
            "icd10": "D64.9",       # Anemia, unspecified
            "icd10_display": "Anemia, unspecified",
            "rxnorm": None
        },
        "wbc": {
            "loinc": [
                {"code": "26464-8", "display": "Leukocytes [#/volume] in Blood", "confidence": 0.99}
            ],
            "snomed": "252275004",  # White blood cell count
            "snomed_display": "White blood cell count",
            "icd10": "D72.82",      # Leukocytosis
            "icd10_display": "Elevated white blood cell count",
            "rxnorm": None
        },
        "rbc": {
            "loinc": [
                {"code": "26453-1", "display": "Erythrocytes [#/volume] in Blood", "confidence": 0.99}
            ],
            "snomed": "391552002",  # Red blood cell count
            "snomed_display": "Red blood cell count",
            "icd10": "D75.1",       # Secondary polycythemia
            "icd10_display": "Secondary polycythemia",
            "rxnorm": None
        },
        "tsh": {
            "loinc": [
                {"code": "83063-0", "display": "Thyrotropin [Units/volume] in Serum or Plasma", "confidence": 0.99}
            ],
            "snomed": "365922002",  # Thyroid stimulating hormone measurement
            "snomed_display": "Thyroid stimulating hormone measurement",
            "icd10": "E03.9",       # Hypothyroidism, unspecified
            "icd10_display": "Hypothyroidism, unspecified",
            "rxnorm": None
        },
        "thyroid stimulating hormone": {
            "loinc": [
                {"code": "83063-0", "display": "Thyrotropin [Units/volume] in Serum or Plasma", "confidence": 0.99}
            ],
            "snomed": "365922002",  # Thyroid stimulating hormone measurement
            "snomed_display": "Thyroid stimulating hormone measurement",
            "icd10": "E03.9",       # Hypothyroidism, unspecified
            "icd10_display": "Hypothyroidism, unspecified",
            "rxnorm": None
        },
        "creatinine": {
            "loinc": [
                {"code": "2160-0", "display": "Creatinine [Mass/volume] in Urine", "confidence": 0.99}
            ],
            "snomed": "70901005",   # Urine creatinine measurement
            "snomed_display": "Urine creatinine measurement",
            "icd10": "N18.9",       # Chronic kidney disease
            "icd10_display": "Chronic kidney disease, unspecified",
            "rxnorm": None
        },
        "digoxin": {
            "loinc": [
                {"code": "3558-4", "display": "Digoxin [Mass/volume] in Serum or Plasma", "confidence": 0.99}
            ],
            "snomed": "365824008",  # Serum digoxin measurement
            "snomed_display": "Serum digoxin measurement",
            "icd10": "T46.0X5A",    # Adverse effect of cardiac glycosides
            "icd10_display": "Adverse effect of cardiac-stimulant glycosides, initial encounter",
            "rxnorm": "3407",        # Digoxin clinical drug
            "rxnorm_display": "Digoxin"
        },
        "acetaminophen": {
            "loinc": [
                {"code": "1920-8", "display": "Acetaminophen [Mass/volume] in Serum or Plasma", "confidence": 0.99}
            ],
            "snomed": "365809002",  # Serum acetaminophen measurement
            "snomed_display": "Serum acetaminophen measurement",
            "icd10": "T39.1X5A",    # Adverse effect of 4-Aminophenol derivatives
            "icd10_display": "Adverse effect of 4-Aminophenol derivatives, initial encounter",
            "rxnorm": "21254",       # Acetaminophen clinical drug
            "rxnorm_display": "Acetaminophen"
        }
    }

    _UCUM_DB = {
        "mg/dl": "mg/dL",
        "mmol/l": "mmol/L",
        "g/dl": "g/dL",
        "10*3/ul": "10*3/uL",
        "10*6/ul": "10*6/uL",
        "uiu/ml": "uIU/mL",
        "ng/ml": "ng/mL"
    }

    def __init__(self, loinc_query_engine: Any = None):
        # Allow injecting Google Health's LoincQueryEngine directly
        self.loinc_query_engine = loinc_query_engine

    def resolve_code(
        self,
        analyte_name: str,
        specimen: str | None = None,
        unit: str | None = None
    ) -> TerminologyMapResult:
        term_clean = analyte_name.strip().lower()

        # 1. Resolve LOINC candidates
        loinc_candidates = self._get_loinc_candidates(analyte_name, term_clean, specimen, unit)

        # 2. Extract primary and base alternatives
        primary_loinc = loinc_candidates[0]
        alternatives = loinc_candidates[1:] if len(loinc_candidates) > 1 else []

        # 3. Add UCUM mappings
        self._add_ucum_mapping(unit, alternatives)

        # 4. Add SNOMED, ICD-10, and RxNorm mappings
        self._add_local_db_mappings(term_clean, alternatives)

        return TerminologyMapResult(
            primary_mapping=primary_loinc,
            alternative_mappings=alternatives
        )

    def _get_loinc_candidates(
        self,
        analyte_name: str,
        term_clean: str,
        specimen: str | None,
        unit: str | None
    ) -> list[TerminologyMapping]:
        candidates = []

        # Attempt query engine if loaded
        if self.loinc_query_engine:
            try:
                from src.document_to_fhir.common.schema.resources import LabTest
                test_resource = LabTest(
                    core_analyte=analyte_name,
                    specimen_type=specimen or "",
                    unit=unit or ""
                )
                mdt_rows = self.loinc_query_engine.query(test_resource)
                for idx, row in enumerate(mdt_rows):
                    conf = max(0.1, 1.0 - (idx * 0.1))
                    candidates.append(
                        TerminologyMapping(
                            code=row.loinc_num,
                            display=row.long_common_name,
                            system="LOINC",
                            confidence_score=conf
                        )
                    )
            except Exception as e:
                logger.warning(f"Failed to query Google Health MDT query engine: {str(e)}. Falling back to DB.")

        # Fallback to local high-fidelity database if query yielded nothing
        if not candidates:
            matched_key = self._find_matched_key(term_clean)
            if matched_key:
                entry = self._ANALYTE_DB[matched_key]
                for item in entry["loinc"]:
                    conf = item["confidence"] if term_clean == matched_key else item["confidence"] * 0.90
                    candidates.append(
                        TerminologyMapping(
                            code=item["code"],
                            display=item["display"],
                            system="LOINC",
                            confidence_score=conf
                        )
                    )

        # Fallback default code if still empty
        if not candidates:
            candidates.append(
                TerminologyMapping(
                    code="73999-5",
                    display=f"Analyte extraction: {analyte_name}",
                    system="LOINC",
                    confidence_score=0.1
                )
            )

        return candidates

    def _find_matched_key(self, term_clean: str) -> str | None:
        for key in self._ANALYTE_DB:
            if key in term_clean:
                return key
        return None

    def _add_ucum_mapping(self, unit: str | None, alternatives: list[TerminologyMapping]) -> None:
        if not unit:
            return
        unit_clean = unit.strip().lower()
        ucum_code = self._UCUM_DB.get(unit_clean)
        if ucum_code:
            alternatives.append(
                TerminologyMapping(
                    code=ucum_code,
                    display=f"UCUM unit: {ucum_code}",
                    system="UCUM",
                    confidence_score=0.99
                )
            )

    def _add_local_db_mappings(self, term_clean: str, alternatives: list[TerminologyMapping]) -> None:
        matched_key = self._find_matched_key(term_clean)
        if not matched_key:
            return

        entry = self._ANALYTE_DB[matched_key]
        if entry.get("snomed"):
            alternatives.append(
                TerminologyMapping(
                    code=entry["snomed"],
                    display=entry["snomed_display"],
                    system="SNOMED_CT",
                    confidence_score=0.95
                )
            )
        if entry.get("icd10"):
            alternatives.append(
                TerminologyMapping(
                    code=entry["icd10"],
                    display=entry["icd10_display"],
                    system="ICD_10",
                    confidence_score=0.90
                )
            )
        if entry.get("rxnorm"):
            alternatives.append(
                TerminologyMapping(
                    code=entry["rxnorm"],
                    display=entry["rxnorm_display"],
                    system="RXNORM",
                    confidence_score=0.95
                )
            )
