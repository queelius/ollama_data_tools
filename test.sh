../llm/llamagpu \
	--model ../models/mistral_latest.gguf \
	--prompt prompt.txt \
	--n_predict "[INST] You are a helpful assistant. [/INST]" \
	--stop "[INST]" \
	--stop "[/INST]"
