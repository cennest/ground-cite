import React, { useState, useEffect } from 'react';
import { analysisAPI, configAPI } from '../services/api';
import Header from './Header';
import QueryInput from './QueryInput';
import ResultsDisplay from './ResultsDisplay';
import ConfigurationModal from './ConfigurationModal';
import styles from './styles';
import './Responsive.css';

const QueryAnalysisUI = () => {
    const [query, setQuery] = useState('');
    const [systemInstruction, setSystemInstruction] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);
    const [backendStatus, setBackendStatus] = useState('checking');
    const [focusedInput, setFocusedInput] = useState(false);
    const [configModalOpen, setConfigModalOpen] = useState(false);

    const [apiKeys, setApiKeys] = useState({
        gemini: {
            primary: '',
            secondary: ''
        },
        openai: ''
    });

    const [config, setConfig] = useState({
        validate: false,
        parse: false,
        schema: '{\n  "type": "object",\n  "properties": {\n    "analysis": {\n      "type": "string",\n      "description": "AI analysis result"\n    },\n    "confidence": {\n      "type": "number",\n      "description": "Confidence score"\n    }\n  }\n}',
        siteConfig: {
            includeList: '',
            excludeList: ''
        }
    });

    const [parsingProvider, setParsingProvider] = useState('gemini');

    const [searchModelName, setSearchModelName] = useState('gemini-2.5-flash');
    const [validateModelName, setValidateModelName] = useState('gemini-2.5-flash');
    const [parseModelName, setParseModelName] = useState('gemini-2.5-flash');

    const [searchGeminiParams, setSearchGeminiParams] = useState({
        temperature: 0.7,
        max_output_tokens: 8192,
        top_p: 0.8,
        top_k: 40,
    });

    const [validateGeminiParams, setValidateGeminiParams] = useState({
        temperature: 0.7,
        max_output_tokens: 8192,
        top_p: 0.8,
        top_k: 40,
    });

    const [parsingGeminiParams, setParsingGeminiParams] = useState({
        temperature: 0.7,
        max_output_tokens: 8192,
        top_p: 0.8,
        top_k: 40,
    });

    const [parsingOpenaiParams, setParsingOpenaiParams] = useState({
        reasoning_effort: 'medium',
        max_completion_tokens: 65536
    });

    const [schemaKeys, setSchemaKeys] = useState([
        { key: 'category', type: 'string', required: true, description: 'Primary category' },
        { key: 'confidence', type: 'number', required: false, description: 'Confidence score' },
        { key: 'tags', type: 'array', required: false, description: 'Related tags' }
    ]);

    const [savedConfigs, setSavedConfigs] = useState([]);

    useEffect(() => {
        loadConfigurationsFromBackend();
        checkBackendHealth();
    }, []);

    const checkBackendHealth = async () => {
        try {
            await analysisAPI.healthCheck();
            setBackendStatus('connected');
        } catch (error) {
            setBackendStatus('disconnected');
            setError('AI Service is currently offline. Please check your connection.');
        }
    };

    const loadConfigurationsFromBackend = async () => {
        try {
            const configs = await configAPI.getConfigurations();
            setSavedConfigs(configs);
        } catch (error) {
            console.error('Failed to load configurations:', error);
        }
    };

    const saveConfiguration = async () => {
        const configName = prompt('Enter configuration name:');
        if (configName) {
            try {
                const configData = {
                    name: configName,
                    config,
                    parsing_provider: parsingProvider,
                    search_model_name: searchModelName,
                    validate_model_name: validateModelName,
                    parse_model_name: parseModelName,
                    search_gemini_params: searchGeminiParams,
                    validate_gemini_params: validateGeminiParams,
                    parsing_gemini_params: parsingGeminiParams,
                    parsing_openai_params: parsingOpenaiParams,
                    schema_keys: schemaKeys,
                    api_keys: apiKeys
                };

                await configAPI.saveConfiguration(configData);
                await loadConfigurationsFromBackend();
                setError(null);
            } catch (error) {
                setError('Failed to save configuration: ' + error.message);
            }
        }
    };

    const deleteConfiguration = async (configId) => {
        if (window.confirm('Are you sure you want to delete this configuration?')) {
            try {
                await configAPI.deleteConfiguration(configId);
                await loadConfigurationsFromBackend();
                setError(null);
            } catch (error) {
                setError('Failed to delete configuration: ' + error.message);
            }
        }
    };

    const loadConfiguration = (savedConfig) => {
        console.log('Loading configuration:', savedConfig);

        setConfig(savedConfig.config || config);
        setParsingProvider(savedConfig.parsing_provider || 'gemini');
        setSearchModelName(savedConfig.search_model_name || 'gemini-2.5-flash');
        setValidateModelName(savedConfig.validate_model_name || 'gemini-2.5-flash');
        setParseModelName(savedConfig.parse_model_name || 'gemini-2.5-flash');
        setSearchGeminiParams(savedConfig.search_gemini_params || searchGeminiParams);
        setValidateGeminiParams(savedConfig.validate_gemini_params || validateGeminiParams);
        setParsingGeminiParams(savedConfig.parsing_gemini_params || parsingGeminiParams);
        setParsingOpenaiParams(savedConfig.parsing_openai_params || parsingOpenaiParams);
        setSchemaKeys(savedConfig.schema_keys || schemaKeys);
        setApiKeys(savedConfig.api_keys || apiKeys);

        setConfigModalOpen(false);
        setError(null);
    };

    const exportConfiguration = () => {
        const exportData = {
            config,
            parsingProvider,
            searchModelName,
            validateModelName,
            parseModelName,
            searchGeminiParams,
            validateGeminiParams,
            parsingGeminiParams,
            parsingOpenaiParams,
            schemaKeys,
            apiKeys
        };
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'ai-analysis-config.json';
        a.click();
    };

    const importConfiguration = (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const imported = JSON.parse(e.target.result);
                    setConfig(imported.config || config);
                    setParsingProvider(imported.parsingProvider || 'gemini');
                    setSearchModelName(imported.searchModelName || 'gemini-2.5-flash');
                    setValidateModelName(imported.validateModelName || 'gemini-2.5-flash');
                    setParseModelName(imported.parseModelName || 'gemini-2.5-flash');
                    setSearchGeminiParams(imported.searchGeminiParams || searchGeminiParams);
                    setValidateGeminiParams(imported.validateGeminiParams || validateGeminiParams);
                    setParsingGeminiParams(imported.parsingGeminiParams || parsingGeminiParams);
                    setParsingOpenaiParams(imported.parsingOpenaiParams || parsingOpenaiParams);
                    setSchemaKeys(imported.schemaKeys || schemaKeys);
                    setApiKeys(imported.apiKeys || apiKeys);
                    setError(null);
                } catch (error) {
                    alert('Invalid configuration file');
                }
            };
            reader.readAsText(file);
        }
    };

    const analyzeQuery = async () => {
        if (backendStatus !== 'connected') {
            setError('AI Service is currently offline. Please check your connection.');
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            const requestData = {
                query,
                system_instruction: systemInstruction,
                config,
                parsing_provider: parsingProvider,
                search_model_name: searchModelName,
                validate_model_name: validateModelName,
                parse_model_name: parseModelName,
                search_gemini_params: searchGeminiParams,
                validate_gemini_params: validateGeminiParams,
                parsing_gemini_params: parsingGeminiParams,
                parsing_openai_params: parsingOpenaiParams,
                api_keys: apiKeys
            };

            const response = await analysisAPI.analyzeQuery(requestData);

            if (response.success) {
                setResults({
                    ...response.data,
                    metadata: response.metadata
                });
            } else {
                setError(response.error || 'Analysis failed');
            }
        } catch (error) {
            setError(error.message || 'Failed to analyze query');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="main-container" style={styles.container}>
            <Header
                backendStatus={backendStatus}
                onConfigClick={() => setConfigModalOpen(true)}
                error={error}
                setError={setError}
            />

            <QueryInput
                query={query}
                setQuery={setQuery}
                systemInstruction={systemInstruction}
                setSystemInstruction={setSystemInstruction}
                isLoading={isLoading}
                focusedInput={focusedInput}
                setFocusedInput={setFocusedInput}
                onAnalyze={analyzeQuery}
            />

            <ResultsDisplay results={results} />

            <ConfigurationModal
                isOpen={configModalOpen}
                onClose={() => setConfigModalOpen(false)}
                config={config}
                setConfig={setConfig}
                parsingProvider={parsingProvider}
                setParsingProvider={setParsingProvider}
                searchModelName={searchModelName}
                setSearchModelName={setSearchModelName}
                validateModelName={validateModelName}
                setValidateModelName={setValidateModelName}
                parseModelName={parseModelName}
                setParseModelName={setParseModelName}
                searchGeminiParams={searchGeminiParams}
                setSearchGeminiParams={setSearchGeminiParams}
                validateGeminiParams={validateGeminiParams}
                setValidateGeminiParams={setValidateGeminiParams}
                parsingGeminiParams={parsingGeminiParams}
                setParsingGeminiParams={setParsingGeminiParams}
                parsingOpenaiParams={parsingOpenaiParams}
                setParsingOpenaiParams={setParsingOpenaiParams}
                apiKeys={apiKeys}
                setApiKeys={setApiKeys}
                schemaKeys={schemaKeys}
                setSchemaKeys={setSchemaKeys}
                savedConfigs={savedConfigs}
                onLoadConfigurations={loadConfigurationsFromBackend}
                onSaveConfiguration={saveConfiguration}
                onDeleteConfiguration={deleteConfiguration}
                onLoadConfiguration={loadConfiguration}
                onExportConfiguration={exportConfiguration}
                onImportConfiguration={importConfiguration}
            />
        </div>
    );
};

export default QueryAnalysisUI;