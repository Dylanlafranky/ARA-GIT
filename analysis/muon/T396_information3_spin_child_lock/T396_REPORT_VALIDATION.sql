-- DuckDB reproduction query for the saved independent-validation status.
-- The portable report embeds the flattened checks produced by the report builder.

SELECT
  test_id,
  overall_assessment,
  overall_pass
FROM read_json_auto('T396_VALIDATION.json');
