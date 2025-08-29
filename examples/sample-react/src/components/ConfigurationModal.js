import React, { useState, useEffect } from 'react';
import { Settings, Save, Upload, Download, RefreshCw, CheckCircle, AlertCircle, Trash2, Plus, Eye, Code, Brain, Zap, Activity, X } from 'lucide-react';
import styles from './styles';
import './Responsive.css';

const getGeminiModelDefaults = (model) => {
    const baseDefaults = {
        temperature: 0.7,
        max_output_tokens: 1024,
        top_p: 0.8,
        top_k: 40,
    };

    switch (model) {
        case 'gemini-2.0-flash-exp':
            return { ...baseDefaults, max_output_tokens: 8192, temperature: 0.5 };
        case 'gemini-2.5-pro':
            return { ...baseDefaults, max_output_tokens: 2048, temperature: 0.8 };
        case 'gemini-2.5-flash':
            return { ...baseDefaults, max_output_tokens: 8192, temperature: 0.7 };
        case 'gemini-1.5-pro':
            return { ...baseDefaults, max_output_tokens: 2048, temperature: 0.8 };
        case 'gemini-1.5-flash':
            return { ...baseDefaults, max_output_tokens: 8192, temperature: 0.6 };
        default:
            return baseDefaults;
    }
};

const getOpenAIModelDefaults = (model) => {
    const isOModel = ['o1', 'o1-mini', 'o3-mini'].includes(model);

    if (isOModel) {
        const oDefaults = {
            reasoning_effort: 'medium',
            max_completion_tokens: model === 'o1' ? 100000 : 65536
        };
        return oDefaults;
    }

    const baseDefaults = {
        temperature: 0.7,
        max_tokens: 1024,
        top_p: 1,
        frequency_penalty: 0,
        presence_penalty: 0
    };

    switch (model) {
        case 'gpt-4o':
            return { ...baseDefaults, max_tokens: 4096, temperature: 0.7 };
        case 'gpt-4o-mini':
            return { ...baseDefaults, max_tokens: 16384, temperature: 0.7 };
        case 'gpt-4-turbo':
            return { ...baseDefaults, max_tokens: 4096, temperature: 0.7 };
        case 'gpt-4':
            return { ...baseDefaults, max_tokens: 8192, temperature: 0.7 };
        case 'gpt-3.5-turbo':
            return { ...baseDefaults, max_tokens: 4096, temperature: 0.7 };
        default:
            return baseDefaults;
    }
};

const ConfigurationModal = ({
    isOpen,
    onClose,
    config,
    setConfig,
    parsingProvider,
    setParsingProvider,
    searchModelName,
    setSearchModelName,
    validateModelName,
    setValidateModelName,
    parseModelName,
    setParseModelName,
    searchGeminiParams,
    setSearchGeminiParams,
    validateGeminiParams,
    setValidateGeminiParams,
    parsingGeminiParams,
    setParsingGeminiParams,
    parsingOpenaiParams,
    setParsingOpenaiParams,
    apiKeys,
    setApiKeys,
    schemaKeys,
    setSchemaKeys,
    savedConfigs,
    onLoadConfigurations,
    onSaveConfiguration,
    onDeleteConfiguration,
    onLoadConfiguration,
    onExportConfiguration,
    onImportConfiguration
}) => {
    // Check if API keys are configured to determine default tab
    const hasApiKeys = apiKeys?.gemini?.primary || apiKeys?.gemini?.secondary || apiKeys?.openai;
    const [activeTab, setActiveTab] = useState(hasApiKeys ? 'basic' : 'keys');

    useEffect(() => {
        const style = document.createElement('style');
        style.textContent = `
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    
    @keyframes pulse {
      0%, 100% { 
        opacity: 1; 
        transform: scale(1); 
      }
      50% { 
        opacity: 0.9; 
        transform: scale(1.02); 
      }
    }
    
    @keyframes shimmer {
      0% { background-position: -200% 0; }
      100% { background-position: 200% 0; }
    }
  `;
        document.head.appendChild(style);
        return () => document.head.removeChild(style);
    }, []);

    if (!isOpen) return null;

    const handleConfigChange = (key, value) => {
        setConfig(prev => ({ ...prev, [key]: value }));
    };

    const handleSearchGeminiParamChange = (key, value) => {
        setSearchGeminiParams(prev => ({ ...prev, [key]: value }));
    };

    const handleValidateGeminiParamChange = (key, value) => {
        setValidateGeminiParams(prev => ({ ...prev, [key]: value }));
    };

    const handleParsingGeminiParamChange = (key, value) => {
        setParsingGeminiParams(prev => ({ ...prev, [key]: value }));
    };

    const handleParsingOpenaiParamChange = (key, value) => {
        setParsingOpenaiParams(prev => ({ ...prev, [key]: value }));
    };

    const handleSiteConfigChange = (key, value) => {
        setConfig(prev => ({
            ...prev,
            siteConfig: { ...prev.siteConfig, [key]: value }
        }));
    };

    const addSchemaKey = () => {
        setSchemaKeys(prev => [...prev, { key: '', type: 'string', required: false, description: '' }]);
    };

    const updateSchemaKey = (index, field, value) => {
        setSchemaKeys(prev => prev.map((key, i) =>
            i === index ? { ...key, [field]: value } : key
        ));
    };

    const removeSchemaKey = (index) => {
        setSchemaKeys(prev => prev.filter((_, i) => i !== index));
    };

    const updateGeminiKey = (keyType, value) => {
        setApiKeys(prev => ({
            ...prev,
            gemini: { ...prev.gemini, [keyType]: value }
        }));
    };

    const updateOpenaiKey = (value) => {
        setApiKeys(prev => ({ ...prev, openai: value }));
    };

    const generateSchema = () => {
        const properties = {};
        const required = [];

        schemaKeys.forEach(key => {
            if (key.key) {
                properties[key.key] = {
                    type: key.type,
                    description: key.description
                };
                if (key.required) {
                    required.push(key.key);
                }
            }
        });

        const schema = {
            type: 'object',
            properties,
            ...(required.length > 0 && { required })
        };

        setConfig(prev => ({ ...prev, schema: JSON.stringify(schema, null, 2) }));
        setActiveTab('basic');
    };

    const TabButton = ({ id, label, active, onClick }) => (
        <button
            onClick={() => onClick(id)}
            style={{
                ...styles.tab,
                ...(active ? styles.tabActive : {})
            }}
        >
            {label}
        </button>
    );

    const geminiModels = [
        { value: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash (Default)' },
        { value: 'gemini-2.5-pro', label: 'Gemini 2.5 Pro' },
        { value: 'gemini-2.0-flash-exp', label: 'Gemini 2.0 Flash Experimental' },
        { value: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro' },
        { value: 'gemini-1.5-flash', label: 'Gemini 1.5 Flash' }
    ];

    const openaiModels = [
        { value: 'o3-mini', label: 'O3 Mini (Default)' },
        { value: 'o1', label: 'O1' },
        { value: 'o1-mini', label: 'O1 Mini' },
        { value: 'gpt-4o', label: 'GPT-4o' },
        { value: 'gpt-4o-mini', label: 'GPT-4o Mini' },
        { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
        { value: 'gpt-4', label: 'GPT-4' },
        { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' }
    ];

    return (
        <div className="modal-overlay" style={styles.modalOverlay} onClick={onClose}>
            <div className="modal-content" style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
                <div className="modal-header" style={styles.modalHeader}>
                    <div>
                        <h2 style={{
                            margin: 0,
                            fontSize: '24px',
                            fontWeight: '700',
                            color: '#ffffff'
                        }}>
                            AI Configuration
                        </h2>
                        <p style={{
                            margin: '4px 0 0 0',
                            fontSize: '14px',
                            color: '#a1a1aa'
                        }}>
                            Configure AI models and parameters
                        </p>
                        <div style={{
                            marginTop: '8px',
                            padding: '8px 12px',
                            background: 'rgba(34, 197, 94, 0.1)',
                            borderRadius: '6px',
                            border: '1px solid rgba(34, 197, 94, 0.2)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px'
                        }}>
                            <CheckCircle size={14} style={{ color: '#22c55e' }} />
                            <span style={{
                                fontSize: '12px',
                                color: '#22c55e',
                                fontWeight: '500'
                            }}>
                                Changes apply automatically
                            </span>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        style={{
                            background: 'linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%)',
                            border: 'none',
                            color: '#ffffff',
                            cursor: 'pointer',
                            padding: '10px 16px',
                            borderRadius: '8px',
                            transition: 'all 0.3s ease',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '8px',
                            fontSize: '14px',
                            fontWeight: '600',
                            flexShrink: 0
                        }}
                        onMouseEnter={(e) => {
                            e.target.style.transform = 'translateY(-1px)';
                            e.target.style.boxShadow = '0 4px 12px rgba(0, 212, 255, 0.4)';
                        }}
                        onMouseLeave={(e) => {
                            e.target.style.transform = 'translateY(0)';
                            e.target.style.boxShadow = 'none';
                        }}
                    >
                        <CheckCircle size={16} />
                        {window.innerWidth < 768 ? 'Apply' : 'Apply & Close'}
                    </button>
                </div>

                <div className="modal-body" style={styles.modalBody}>
                    <div className="tabs" style={styles.tabs}>
                        <TabButton
                            id="basic"
                            label="Core Config"
                            active={activeTab === 'basic'}
                            onClick={setActiveTab}
                        />
                        <TabButton
                            id="models"
                            label="AI Models"
                            active={activeTab === 'models'}
                            onClick={setActiveTab}
                        />
                        <TabButton
                            id="schema"
                            label="Schema Designer"
                            active={activeTab === 'schema'}
                            onClick={setActiveTab}
                        />
                        {/* <TabButton
                            id="saved"
                            label="Saved Configs"
                            active={activeTab === 'saved'}
                            onClick={setActiveTab}
                        /> */}
                        <TabButton
                            id="keys"
                            label="API Keys"
                            active={activeTab === 'keys'}
                            onClick={setActiveTab}
                        />
                    </div>

                    <div className="config-actions" style={styles.configActions}>
                        {/* <button onClick={onSaveConfiguration} style={{ ...styles.smallButton, ...styles.buttonSuccess }}>
                            <Save size={14} />
                            Save Config
                        </button> */}
                        {/* <button onClick={onExportConfiguration} style={{ ...styles.smallButton, ...styles.buttonSecondary }}>
                            <Download size={14} />
                            Export
                        </button> */}
                        <label style={{ ...styles.smallButton, ...styles.buttonSecondary, cursor: 'pointer' }}>
                            <Upload size={14} />
                            Import
                            <input type="file" accept=".json" onChange={onImportConfiguration} style={{ display: 'none' }} />
                        </label>
                    </div>

                    <div className="config-panel" style={styles.configPanel}>
                        {activeTab === 'basic' && (
                            <div>
                                <h3 style={styles.sectionTitle}>
                                    <Settings size={18} />
                                    Core Configuration
                                </h3>

                                <div style={{ ...styles.grid, ...styles.gridCols2 }}>
                                    <div>
                                        <div style={{ marginBottom: '20px' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                                                <input
                                                    type="checkbox"
                                                    id="validate"
                                                    checked={config.validate}
                                                    onChange={(e) => handleConfigChange('validate', e.target.checked)}
                                                    style={styles.checkbox}
                                                />
                                                <label htmlFor="validate" style={{
                                                    fontSize: window.innerWidth < 768 ? '13px' : '15px',
                                                    fontWeight: '600',
                                                    color: '#e4e4e7'
                                                }}>
                                                    Enable Response Validation
                                                </label>
                                            </div>
                                            <p style={{
                                                fontSize: window.innerWidth < 768 ? '11px' : '13px',
                                                color: '#a1a1aa',
                                                marginLeft: window.innerWidth < 768 ? '24px' : '30px',
                                                lineHeight: '1.4'
                                            }}>
                                                Validate AI responses against the received citations
                                            </p>
                                        </div>

                                        <div style={{ marginBottom: '20px' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                                                <input
                                                    type="checkbox"
                                                    id="parse"
                                                    checked={config.parse}
                                                    onChange={(e) => handleConfigChange('parse', e.target.checked)}
                                                    style={styles.checkbox}
                                                />
                                                <label htmlFor="parse" style={{
                                                    fontSize: window.innerWidth < 768 ? '13px' : '15px',
                                                    fontWeight: '600',
                                                    color: '#e4e4e7'
                                                }}>
                                                    Enable Structured JSON Output
                                                </label>
                                            </div>
                                            <p style={{
                                                fontSize: window.innerWidth < 768 ? '11px' : '13px',
                                                color: '#a1a1aa',
                                                marginLeft: window.innerWidth < 768 ? '24px' : '30px',
                                                lineHeight: '1.4'
                                            }}>
                                                Advanced AI response structuring
                                            </p>
                                        </div>

                                        <div style={{
                                            marginBottom: '20px',
                                            padding: window.innerWidth < 768 ? '16px' : '20px',
                                            background: 'rgba(255, 255, 255, 0.02)',
                                            borderRadius: window.innerWidth < 768 ? '8px' : '12px',
                                            border: '1px solid rgba(255, 255, 255, 0.1)'
                                        }}>
                                            <h4 style={{
                                                fontSize: window.innerWidth < 768 ? '14px' : '16px',
                                                fontWeight: '600',
                                                color: '#e4e4e7',
                                                marginBottom: '12px'
                                            }}>
                                                Site Configuration
                                            </h4>

                                            <div style={{ marginBottom: '12px' }}>
                                                <label style={styles.label}>Include Sites (one per line)</label>
                                                <textarea
                                                    value={config.siteConfig?.includeList || ''}
                                                    onChange={(e) => handleSiteConfigChange('includeList', e.target.value)}
                                                    placeholder="https://www.example.com&#10;https://www.news.com&#10;https://www.wikipedia.org"
                                                    rows={3}
                                                    style={styles.textarea}
                                                />
                                            </div>

                                            <div style={{ marginBottom: '12px' }}>
                                                <label style={styles.label}>Exclude Sites (one per line)</label>
                                                <textarea
                                                    value={config.siteConfig?.excludeList || ''}
                                                    onChange={(e) => handleSiteConfigChange('excludeList', e.target.value)}
                                                    placeholder="https://www.spam.com&#10;https://www.badsite.net&#10;https://www.unwanted.org"
                                                    rows={3}
                                                    style={styles.textarea}
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    <div>
                                        <label style={styles.label}>JSON Schema Definition</label>
                                        <textarea
                                            value={config.schema || ''}
                                            onChange={(e) => handleConfigChange('schema', e.target.value)}
                                            rows={window.innerWidth < 768 ? 12 : 18}
                                            style={styles.textarea}
                                            placeholder="Define your JSON schema..."
                                        />
                                    </div>
                                </div>
                            </div>
                        )}

                        {activeTab === 'models' && (
                            <div>
                                <h3 style={styles.sectionTitle}>
                                    <Activity size={18} />
                                    AI Model Configuration
                                </h3>

                                <div style={{
                                    marginBottom: '24px',
                                    padding: window.innerWidth < 768 ? '16px' : '20px',
                                    background: 'rgba(0, 212, 255, 0.05)',
                                    borderRadius: window.innerWidth < 768 ? '8px' : '12px',
                                    border: '1px solid rgba(0, 212, 255, 0.2)'
                                }}>
                                    <h4 style={{
                                        fontSize: window.innerWidth < 768 ? '14px' : '18px',
                                        fontWeight: '600',
                                        color: '#00d4ff',
                                        marginBottom: '12px',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '6px'
                                    }}>
                                        <Zap size={16} />
                                        Search Model (Gemini)
                                    </h4>
                                    <div style={{ ...styles.grid, ...styles.gridCols3 }}>
                                        <div>
                                            <label style={styles.label}>Model</label>
                                            <select
                                                value={searchModelName}
                                                onChange={(e) => setSearchModelName(e.target.value)}
                                                style={styles.select}
                                            >
                                                {geminiModels.map(model => (
                                                    <option key={model.value} style={styles.option} value={model.value}>
                                                        {model.label}
                                                    </option>
                                                ))}
                                            </select>
                                        </div>

                                        <div>
                                            <label style={styles.label}>
                                                Temperature: {searchGeminiParams.temperature}
                                            </label>
                                            <input
                                                type="range"
                                                min="0"
                                                max="1"
                                                step="0.1"
                                                value={searchGeminiParams.temperature}
                                                onChange={(e) => handleSearchGeminiParamChange('temperature', parseFloat(e.target.value))}
                                                style={styles.slider}
                                            />
                                        </div>

                                        <div>
                                            <label style={styles.label}>Max Tokens</label>
                                            <input
                                                type="number"
                                                value={searchGeminiParams.max_output_tokens}
                                                onChange={(e) => handleSearchGeminiParamChange('max_output_tokens', parseInt(e.target.value))}
                                                style={styles.input}
                                            />
                                        </div>
                                    </div>
                                </div>

                                <div style={{
                                    marginBottom: '24px',
                                    padding: window.innerWidth < 768 ? '16px' : '20px',
                                    background: 'rgba(16, 185, 129, 0.05)',
                                    borderRadius: window.innerWidth < 768 ? '8px' : '12px',
                                    border: '1px solid rgba(16, 185, 129, 0.2)'
                                }}>
                                    <h4 style={{
                                        fontSize: window.innerWidth < 768 ? '14px' : '18px',
                                        fontWeight: '600',
                                        color: '#10b981',
                                        marginBottom: '12px',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '6px'
                                    }}>
                                        <CheckCircle size={16} />
                                        Validation Model (Gemini)
                                    </h4>
                                    <div style={{ ...styles.grid, ...styles.gridCols3 }}>
                                        <div>
                                            <label style={styles.label}>Model</label>
                                            <select
                                                value={validateModelName}
                                                onChange={(e) => setValidateModelName(e.target.value)}
                                                style={styles.select}
                                            >
                                                {geminiModels.map(model => (
                                                    <option key={model.value} style={styles.option} value={model.value}>
                                                        {model.label}
                                                    </option>
                                                ))}
                                            </select>
                                        </div>

                                        <div>
                                            <label style={styles.label}>
                                                Temperature: {validateGeminiParams.temperature}
                                            </label>
                                            <input
                                                type="range"
                                                min="0"
                                                max="1"
                                                step="0.1"
                                                value={validateGeminiParams.temperature}
                                                onChange={(e) => handleValidateGeminiParamChange('temperature', parseFloat(e.target.value))}
                                                style={styles.slider}
                                            />
                                        </div>

                                        <div>
                                            <label style={styles.label}>Max Tokens</label>
                                            <input
                                                type="number"
                                                value={validateGeminiParams.max_output_tokens}
                                                onChange={(e) => handleValidateGeminiParamChange('max_output_tokens', parseInt(e.target.value))}
                                                style={styles.input}
                                            />
                                        </div>
                                    </div>
                                </div>

                                <div style={{
                                    marginBottom: '24px',
                                    padding: window.innerWidth < 768 ? '16px' : '20px',
                                    background: 'rgba(124, 58, 237, 0.05)',
                                    borderRadius: window.innerWidth < 768 ? '8px' : '12px',
                                    border: '1px solid rgba(124, 58, 237, 0.2)'
                                }}>
                                    <h4 style={{
                                        fontSize: window.innerWidth < 768 ? '14px' : '18px',
                                        fontWeight: '600',
                                        color: '#7c3aed',
                                        marginBottom: '12px',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '6px'
                                    }}>
                                        <Code size={16} />
                                        Parsing Model Configuration
                                    </h4>

                                    <div style={{ marginBottom: '16px' }}>
                                        <label style={styles.label}>Parsing Provider</label>
                                        <select
                                            value={parsingProvider}
                                            onChange={(e) => {
                                                setParsingProvider(e.target.value)
                                                if (e.target.value === 'gemini') {
                                                    setParseModelName('gemini-2.5-flash')
                                                } else {
                                                    setParseModelName('o3-mini')
                                                }
                                            }}
                                            style={styles.select}
                                        >
                                            <option style={styles.option} value="gemini">Google Gemini</option>
                                            <option style={styles.option} value="openai">OpenAI</option>
                                        </select>
                                    </div>

                                    <div style={{ marginBottom: '16px' }}>
                                        <label style={styles.label}>Parse Model</label>
                                        <select
                                            value={parseModelName}
                                            onChange={(e) => setParseModelName(e.target.value)}
                                            style={styles.select}
                                        >
                                            {parsingProvider === 'gemini' ?
                                                geminiModels.map(model => (
                                                    <option key={model.value} style={styles.option} value={model.value}>
                                                        {model.label}
                                                    </option>
                                                )) :
                                                openaiModels.map(model => (
                                                    <option key={model.value} style={styles.option} value={model.value}>
                                                        {model.label}
                                                    </option>
                                                ))
                                            }
                                        </select>
                                    </div>

                                    {parsingProvider === 'gemini' && (
                                        <div>
                                            <h5 style={{
                                                fontSize: window.innerWidth < 768 ? '13px' : '16px',
                                                fontWeight: '600',
                                                color: '#e4e4e7',
                                                marginBottom: '12px'
                                            }}>
                                                Gemini Parsing Parameters
                                            </h5>
                                            <div style={{ ...styles.grid, ...styles.gridCols3 }}>
                                                <div>
                                                    <label style={styles.label}>
                                                        Temperature: {parsingGeminiParams.temperature}
                                                    </label>
                                                    <input
                                                        type="range"
                                                        min="0"
                                                        max="1"
                                                        step="0.1"
                                                        value={parsingGeminiParams.temperature}
                                                        onChange={(e) => handleParsingGeminiParamChange('temperature', parseFloat(e.target.value))}
                                                        style={styles.slider}
                                                    />
                                                </div>

                                                <div>
                                                    <label style={styles.label}>Max Tokens</label>
                                                    <input
                                                        type="number"
                                                        value={parsingGeminiParams.max_output_tokens}
                                                        onChange={(e) => handleParsingGeminiParamChange('max_output_tokens', parseInt(e.target.value))}
                                                        style={styles.input}
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {parsingProvider === 'openai' && (
                                        <div>
                                            <h5 style={{
                                                fontSize: window.innerWidth < 768 ? '13px' : '16px',
                                                fontWeight: '600',
                                                color: '#e4e4e7',
                                                marginBottom: '12px'
                                            }}>
                                                OpenAI Parsing Parameters
                                            </h5>
                                            {(() => {
                                                const isOModel = ['o1', 'o1-mini', 'o3-mini'].includes(parseModelName);

                                                if (isOModel) {
                                                    return (
                                                        <div className="modal main-container">
                                                            <div style={{ ...styles.grid, ...styles.gridCols3 }}>
                                                                <div>
                                                                    <label style={styles.label}>Reasoning Effort</label>
                                                                    <select
                                                                        value={parsingOpenaiParams.reasoning_effort || 'medium'}
                                                                        onChange={(e) => handleParsingOpenaiParamChange('reasoning_effort', e.target.value)}
                                                                        style={styles.select}
                                                                    >
                                                                        <option style={styles.option} value="low">Low</option>
                                                                        <option style={styles.option} value="medium">Medium</option>
                                                                        <option style={styles.option} value="high">High</option>
                                                                    </select>
                                                                </div>
                                                                <div>
                                                                    <label style={styles.label}>Max Completion Tokens</label>
                                                                    <input
                                                                        type="number"
                                                                        value={parsingOpenaiParams.max_completion_tokens || 65536}
                                                                        onChange={(e) => handleParsingOpenaiParamChange('max_completion_tokens', parseInt(e.target.value))}
                                                                        style={styles.input}
                                                                    />
                                                                </div>
                                                            </div>
                                                        </div>);
                                                } else {
                                                    return (
                                                        <div style={{ ...styles.grid, ...styles.gridCols3 }}>
                                                            <div>
                                                                <label style={styles.label}>
                                                                    Temperature: {parsingOpenaiParams.temperature || 0.7}
                                                                </label>
                                                                <input
                                                                    type="range"
                                                                    min="0"
                                                                    max="2"
                                                                    step="0.1"
                                                                    value={parsingOpenaiParams.temperature || 0.7}
                                                                    onChange={(e) => handleParsingOpenaiParamChange('temperature', parseFloat(e.target.value))}
                                                                    style={styles.slider}
                                                                />
                                                            </div>
                                                            <div>
                                                                <label style={styles.label}>Max Tokens</label>
                                                                <input
                                                                    type="number"
                                                                    value={parsingOpenaiParams.max_tokens || 1024}
                                                                    onChange={(e) => handleParsingOpenaiParamChange('max_tokens', parseInt(e.target.value))}
                                                                    style={styles.input}
                                                                />
                                                            </div>
                                                        </div>
                                                    );
                                                }
                                            })()}
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}

                        {activeTab === 'schema' && (
                            <div>
                                <div style={{
                                    display: 'flex',
                                    flexDirection: window.innerWidth < 768 ? 'column' : 'row',
                                    justifyContent: 'space-between',
                                    alignItems: window.innerWidth < 768 ? 'flex-start' : 'center',
                                    marginBottom: '24px',
                                    gap: window.innerWidth < 768 ? '16px' : '0'
                                }}>
                                    <h3 style={styles.sectionTitle}>
                                        <Code size={18} />
                                        Schema Designer
                                    </h3>
                                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                                        <button
                                            onClick={addSchemaKey}
                                            style={{
                                                ...styles.button,
                                                fontSize: window.innerWidth < 768 ? '12px' : '14px',
                                                padding: window.innerWidth < 768 ? '10px 16px' : '12px 20px'
                                            }}
                                        >
                                            <Plus size={14} />
                                            Add Field
                                        </button>
                                        <button
                                            onClick={generateSchema}
                                            style={{
                                                ...styles.button,
                                                ...styles.buttonSuccess,
                                                fontSize: window.innerWidth < 768 ? '12px' : '14px',
                                                padding: window.innerWidth < 768 ? '10px 16px' : '12px 20px'
                                            }}
                                        >
                                            <Code size={14} />
                                            Generate
                                        </button>
                                    </div>
                                </div>

                                {/* Helper Text */}
                                <div style={{
                                    marginBottom: '20px',
                                    padding: window.innerWidth < 768 ? '12px' : '16px',
                                    background: 'rgba(0, 212, 255, 0.05)',
                                    borderRadius: window.innerWidth < 768 ? '6px' : '8px',
                                    border: '1px solid rgba(0, 212, 255, 0.2)',
                                    display: 'flex',
                                    alignItems: 'flex-start',
                                    gap: '10px'
                                }}>
                                    <div style={{
                                        background: 'rgba(0, 212, 255, 0.2)',
                                        borderRadius: '50%',
                                        padding: '4px',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        minWidth: '24px',
                                        height: '24px',
                                        flexShrink: 0
                                    }}>
                                        <span style={{ fontSize: '12px' }}>💡</span>
                                    </div>
                                    <div>
                                        <p style={{
                                            color: 'rgba(255, 255, 255, 0.9)',
                                            fontSize: window.innerWidth < 768 ? '12px' : '14px',
                                            margin: 0,
                                            lineHeight: '1.4'
                                        }}>
                                            <strong style={{ color: '#00d4ff' }}>How to use:</strong> Add your desired fields using "Add Field", then click <strong style={{ color: '#22c55e' }}>"Generate"</strong> to apply the schema to the Core Config tab.
                                        </p>
                                    </div>
                                </div>

                                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                                    {schemaKeys.map((key, index) => (
                                        window.innerWidth < 768 ? (
                                            // Mobile layout - vertical stack
                                            <div key={index} style={{
                                                display: 'flex',
                                                flexDirection: 'column',
                                                gap: '8px',
                                                padding: '12px',
                                                background: 'rgba(255, 255, 255, 0.02)',
                                                border: '1px solid rgba(255, 255, 255, 0.1)',
                                                borderRadius: '8px',
                                                marginBottom: '8px'
                                            }}>
                                                <div>
                                                    <label style={styles.schemaKeyLabel}>Field Name</label>
                                                    <input
                                                        type="text"
                                                        placeholder="Field name"
                                                        value={key.key}
                                                        onChange={(e) => updateSchemaKey(index, 'key', e.target.value)}
                                                        style={{ ...styles.input, ...styles.schemaKeyInput }}
                                                    />
                                                </div>

                                                <div>
                                                    <label style={styles.schemaKeyLabel}>Type</label>
                                                    <select
                                                        value={key.type}
                                                        onChange={(e) => updateSchemaKey(index, 'type', e.target.value)}
                                                        style={{ ...styles.select, ...styles.schemaKeyInput }}
                                                    >
                                                        <option style={styles.option} value="string">String</option>
                                                        <option style={styles.option} value="number">Number</option>
                                                        <option style={styles.option} value="boolean">Boolean</option>
                                                        <option style={styles.option} value="array">Array</option>
                                                        <option style={styles.option} value="object">Object</option>
                                                    </select>
                                                </div>

                                                <div>
                                                    <label style={styles.schemaKeyLabel}>Description</label>
                                                    <input
                                                        type="text"
                                                        placeholder="Description"
                                                        value={key.description}
                                                        onChange={(e) => updateSchemaKey(index, 'description', e.target.value)}
                                                        style={{ ...styles.input, ...styles.schemaKeyInput }}
                                                    />
                                                </div>

                                                <div style={{
                                                    display: 'flex',
                                                    justifyContent: 'space-between',
                                                    alignItems: 'center',
                                                    marginTop: '4px'
                                                }}>
                                                    <div style={{
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        gap: '6px'
                                                    }}>
                                                        <input
                                                            type="checkbox"
                                                            checked={key.required}
                                                            onChange={(e) => updateSchemaKey(index, 'required', e.target.checked)}
                                                            style={styles.checkbox}
                                                        />
                                                        <label style={{
                                                            fontSize: '11px',
                                                            fontWeight: '500',
                                                            color: '#a1a1aa'
                                                        }}>
                                                            Required
                                                        </label>
                                                    </div>

                                                    <button
                                                        onClick={() => removeSchemaKey(index)}
                                                        style={{
                                                            ...styles.smallButton,
                                                            ...styles.buttonDanger,
                                                            padding: '6px 8px',
                                                            fontSize: '11px'
                                                        }}
                                                    >
                                                        <Trash2 size={12} />
                                                        Remove
                                                    </button>
                                                </div>
                                            </div>
                                        ) : (
                                            // Desktop layout - horizontal grid
                                            <div key={index} style={styles.schemaKeyRow}>
                                                <input
                                                    type="text"
                                                    placeholder="Field name"
                                                    value={key.key}
                                                    onChange={(e) => updateSchemaKey(index, 'key', e.target.value)}
                                                    style={styles.input}
                                                />

                                                <select
                                                    value={key.type}
                                                    onChange={(e) => updateSchemaKey(index, 'type', e.target.value)}
                                                    style={styles.select}
                                                >
                                                    <option style={styles.option} value="string">String</option>
                                                    <option style={styles.option} value="number">Number</option>
                                                    <option style={styles.option} value="boolean">Boolean</option>
                                                    <option style={styles.option} value="array">Array</option>
                                                    <option style={styles.option} value="object">Object</option>
                                                </select>

                                                <input
                                                    type="text"
                                                    placeholder="Description"
                                                    value={key.description}
                                                    onChange={(e) => updateSchemaKey(index, 'description', e.target.value)}
                                                    style={styles.input}
                                                />

                                                <div style={{
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    gap: '4px'
                                                }}>
                                                    <input
                                                        type="checkbox"
                                                        checked={key.required}
                                                        onChange={(e) => updateSchemaKey(index, 'required', e.target.checked)}
                                                        style={styles.checkbox}
                                                    />
                                                    <label style={{
                                                        fontSize: '12px',
                                                        fontWeight: '500',
                                                        color: '#a1a1aa'
                                                    }}>
                                                        Required
                                                    </label>
                                                </div>

                                                <button
                                                    onClick={() => removeSchemaKey(index)}
                                                    style={{ ...styles.smallButton, ...styles.buttonDanger }}
                                                >
                                                    <Trash2 size={14} />
                                                </button>
                                            </div>
                                        )
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* {activeTab === 'saved' && (
                            <div>
                                <div style={{
                                    display: 'flex',
                                    flexDirection: window.innerWidth < 768 ? 'column' : 'row',
                                    justifyContent: 'space-between',
                                    alignItems: window.innerWidth < 768 ? 'flex-start' : 'center',
                                    marginBottom: '24px',
                                    gap: window.innerWidth < 768 ? '16px' : '0'
                                }}>
                                    <h3 style={styles.sectionTitle}>
                                        <Save size={18} />
                                        Saved Configurations
                                    </h3>
                                    <button
                                        onClick={onLoadConfigurations}
                                        style={{
                                            ...styles.button,
                                            fontSize: window.innerWidth < 768 ? '12px' : '14px',
                                            padding: window.innerWidth < 768 ? '10px 16px' : '12px 20px'
                                        }}
                                    >
                                        <RefreshCw size={14} />
                                        Refresh
                                    </button>
                                </div>

                                {savedConfigs.length === 0 ? (
                                    <div style={{ textAlign: 'center', padding: window.innerWidth < 768 ? '32px 0' : '48px 0' }}>
                                        <Settings size={window.innerWidth < 768 ? 32 : 48} color="#52525b" style={{ marginBottom: '12px' }} />
                                        <p style={{
                                            color: '#a1a1aa',
                                            fontSize: window.innerWidth < 768 ? '14px' : '16px',
                                            fontWeight: '500'
                                        }}>
                                            No saved configurations
                                        </p>
                                        <p style={{
                                            color: '#71717a',
                                            fontSize: window.innerWidth < 768 ? '12px' : '14px'
                                        }}>
                                            Create and save your first AI configuration
                                        </p>
                                    </div>
                                ) : (
                                    <div style={styles.cardGrid}>
                                        {savedConfigs.map((savedConfig, index) => (
                                            <div
                                                key={savedConfig.id || index}
                                                style={styles.card}
                                                onMouseEnter={(e) => Object.assign(e.currentTarget.style, styles.cardHover)}
                                                onMouseLeave={(e) => Object.assign(e.currentTarget.style, styles.card)}
                                            >
                                                <h4 style={{
                                                    fontWeight: '600',
                                                    color: '#ffffff',
                                                    marginBottom: '6px',
                                                    fontSize: window.innerWidth < 768 ? '14px' : '16px'
                                                }}>
                                                    {savedConfig.name}
                                                </h4>
                                                <p style={{
                                                    fontSize: window.innerWidth < 768 ? '12px' : '14px',
                                                    color: '#a1a1aa',
                                                    marginBottom: '12px'
                                                }}>
                                                    Created: {savedConfig.created_at ? new Date(savedConfig.created_at).toLocaleDateString() : 'Unknown'}
                                                </p>
                                                <div style={{ display: 'flex', gap: '8px' }}>
                                                    <button
                                                        onClick={() => onLoadConfiguration(savedConfig)}
                                                        style={{
                                                            ...styles.button,
                                                            flex: 1,
                                                            fontSize: window.innerWidth < 768 ? '12px' : '14px',
                                                            padding: window.innerWidth < 768 ? '8px 12px' : '10px 16px'
                                                        }}
                                                    >
                                                        <Eye size={14} />
                                                        Load
                                                    </button>
                                                    {savedConfig.id && (
                                                        <button
                                                            onClick={() => onDeleteConfiguration(savedConfig.id)}
                                                            style={{
                                                                ...styles.smallButton,
                                                                ...styles.buttonDanger,
                                                                padding: window.innerWidth < 768 ? '8px 10px' : '10px 14px'
                                                            }}
                                                        >
                                                            <Trash2 size={14} />
                                                        </button>
                                                    )}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )} */}

                        {activeTab === 'keys' && (
                            <div>
                                <h3 style={styles.sectionTitle}>
                                    <Brain size={18} />
                                    API Keys Configuration
                                </h3>

                                {/* Help Section */}
                                <div style={{
                                    marginBottom: '24px',
                                    padding: window.innerWidth < 768 ? '16px' : '20px',
                                    background: 'linear-gradient(135deg, rgba(255, 193, 7, 0.08) 0%, rgba(255, 152, 0, 0.08) 100%)',
                                    borderRadius: window.innerWidth < 768 ? '8px' : '12px',
                                    border: '1px solid rgba(255, 193, 7, 0.2)'
                                }}>
                                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
                                        <div style={{
                                            background: 'rgba(255, 193, 7, 0.2)',
                                            borderRadius: '50%',
                                            padding: '8px',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            minWidth: '36px',
                                            height: '36px'
                                        }}>
                                            <span style={{ fontSize: '16px' }}>💡</span>
                                        </div>
                                        <div style={{ flex: 1 }}>
                                            <h4 style={{
                                                color: '#ffc107',
                                                margin: '0 0 8px 0',
                                                fontSize: window.innerWidth < 768 ? '14px' : '16px',
                                                fontWeight: '600'
                                            }}>
                                                GroundCite API Configuration
                                            </h4>
                                            <p style={{
                                                color: 'rgba(255, 255, 255, 0.9)',
                                                margin: '0 0 12px 0',
                                                fontSize: window.innerWidth < 768 ? '12px' : '14px',
                                                lineHeight: '1.5'
                                            }}>
                                                GroundCite is powered by Google Gemini. A Gemini API key is required for search functionality. OpenAI is optional for advanced parsing features only if the parsing type is OpenAI selected.
                                            </p>
                                            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
                                                <a
                                                    href="https://makersuite.google.com/app/apikey"
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    style={{
                                                        background: 'linear-gradient(135deg, #00d4ff, #7c3aed)',
                                                        border: 'none',
                                                        borderRadius: '6px',
                                                        padding: '8px 16px',
                                                        color: '#fff',
                                                        textDecoration: 'none',
                                                        fontSize: window.innerWidth < 768 ? '11px' : '13px',
                                                        fontWeight: '600',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        gap: '6px',
                                                        transition: 'all 0.2s ease'
                                                    }}
                                                    onMouseEnter={(e) => {
                                                        e.target.style.transform = 'translateY(-1px)';
                                                        e.target.style.boxShadow = '0 4px 12px rgba(0, 212, 255, 0.3)';
                                                    }}
                                                    onMouseLeave={(e) => {
                                                        e.target.style.transform = 'translateY(0)';
                                                        e.target.style.boxShadow = 'none';
                                                    }}
                                                >
                                                    🚀 Get Gemini API Key (Required)
                                                </a>
                                                <a
                                                    href="https://platform.openai.com/api-keys"
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    style={{
                                                        background: 'transparent',
                                                        border: '1px solid rgba(255, 255, 255, 0.2)',
                                                        borderRadius: '6px',
                                                        padding: '8px 16px',
                                                        color: 'rgba(255, 255, 255, 0.8)',
                                                        textDecoration: 'none',
                                                        fontSize: window.innerWidth < 768 ? '11px' : '13px',
                                                        fontWeight: '500',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        gap: '6px',
                                                        transition: 'all 0.2s ease'
                                                    }}
                                                    onMouseEnter={(e) => {
                                                        e.target.style.borderColor = 'rgba(255, 255, 255, 0.4)';
                                                        e.target.style.color = 'rgba(255, 255, 255, 1)';
                                                    }}
                                                    onMouseLeave={(e) => {
                                                        e.target.style.borderColor = 'rgba(255, 255, 255, 0.2)';
                                                        e.target.style.color = 'rgba(255, 255, 255, 0.8)';
                                                    }}
                                                >
                                                    ⚡ Get OpenAI API Key (Optional)
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Privacy Notice */}
                                <div style={{
                                    marginBottom: '24px',
                                    padding: window.innerWidth < 768 ? '12px' : '16px',
                                    background: 'rgba(34, 197, 94, 0.05)',
                                    borderRadius: window.innerWidth < 768 ? '6px' : '8px',
                                    border: '1px solid rgba(34, 197, 94, 0.2)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '12px'
                                }}>
                                    <div style={{
                                        background: 'rgba(34, 197, 94, 0.2)',
                                        borderRadius: '50%',
                                        padding: '6px',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        minWidth: '32px',
                                        height: '32px'
                                    }}>
                                        <span style={{ fontSize: '14px' }}>🔒</span>
                                    </div>
                                    <div>
                                        <p style={{
                                            color: 'rgba(255, 255, 255, 0.9)',
                                            fontSize: window.innerWidth < 768 ? '12px' : '14px',
                                            margin: 0,
                                            fontWeight: '500'
                                        }}>
                                            <strong>Privacy Protected:</strong> Your API keys are not stored anywhere and will be removed on browser reload
                                        </p>
                                    </div>
                                </div>

                                <div style={{
                                    marginBottom: '24px',
                                    padding: window.innerWidth < 768 ? '16px' : '24px',
                                    background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(124, 58, 237, 0.05) 100%)',
                                    borderRadius: window.innerWidth < 768 ? '8px' : '16px',
                                    border: '1px solid rgba(0, 212, 255, 0.2)',
                                    position: 'relative',
                                    overflow: 'hidden'
                                }}>
                                    <div style={{
                                        position: 'absolute',
                                        top: 0,
                                        left: 0,
                                        right: 0,
                                        height: '2px',
                                        background: 'linear-gradient(90deg, #00d4ff, #7c3aed)',
                                        opacity: 0.6
                                    }}></div>

                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                                        <div style={{
                                            width: window.innerWidth < 768 ? '32px' : '40px',
                                            height: window.innerWidth < 768 ? '32px' : '40px',
                                            background: 'linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%)',
                                            borderRadius: '8px',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center'
                                        }}>
                                            <Brain size={window.innerWidth < 768 ? 16 : 20} color="white" />
                                        </div>
                                        <div>
                                            <h4 style={{
                                                fontSize: window.innerWidth < 768 ? '14px' : '18px',
                                                fontWeight: '700',
                                                color: '#ffffff',
                                                margin: 0
                                            }}>
                                                Google Gemini (Required)
                                            </h4>
                                            <p style={{
                                                fontSize: window.innerWidth < 768 ? '11px' : '14px',
                                                color: '#a1a1aa',
                                                margin: 0
                                            }}>
                                                Core AI engine for search and analysis
                                            </p>
                                        </div>
                                    </div>

                                    <div style={{
                                        display: 'grid',
                                        gap: '16px',
                                        gridTemplateColumns: window.innerWidth < 768 ? '1fr' : 'repeat(auto-fit, minmax(300px, 1fr))'
                                    }}>
                                        <div>
                                            <label style={{
                                                ...styles.label,
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '6px',
                                                color: '#00d4ff'
                                            }}>
                                                <Zap size={12} />
                                                Primary Key
                                            </label>
                                            <div style={{ position: 'relative' }}>
                                                <input
                                                    type="password"
                                                    placeholder="sk-gemini-primary-key..."
                                                    value={apiKeys?.gemini?.primary}
                                                    onChange={(e) => updateGeminiKey('primary', e.target.value)}
                                                    style={{
                                                        ...styles.input,
                                                        paddingLeft: window.innerWidth < 768 ? '36px' : '48px',
                                                        background: 'rgba(0, 0, 0, 0.4)',
                                                        border: '1px solid rgba(0, 212, 255, 0.3)',
                                                        borderRadius: window.innerWidth < 768 ? '8px' : '12px'
                                                    }}
                                                />
                                                <CheckCircle
                                                    size={window.innerWidth < 768 ? 14 : 16}
                                                    style={{
                                                        position: 'absolute',
                                                        left: window.innerWidth < 768 ? '12px' : '16px',
                                                        top: '50%',
                                                        transform: 'translateY(-50%)',
                                                        color: apiKeys.gemini.primary ? '#00ff88' : '#71717a'
                                                    }}
                                                />
                                            </div>
                                        </div>

                                        <div>
                                            <label style={{
                                                ...styles.label,
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '6px',
                                                color: '#a1a1aa'
                                            }}>
                                                <RefreshCw size={12} />
                                                Secondary Key (Backup)
                                            </label>
                                            <div style={{ position: 'relative' }}>
                                                <input
                                                    type="password"
                                                    placeholder="sk-gemini-backup-key..."
                                                    value={apiKeys?.gemini?.secondary}
                                                    onChange={(e) => updateGeminiKey('secondary', e.target.value)}
                                                    style={{
                                                        ...styles.input,
                                                        paddingLeft: window.innerWidth < 768 ? '36px' : '48px',
                                                        background: 'rgba(0, 0, 0, 0.4)',
                                                        border: '1px solid rgba(161, 161, 170, 0.3)',
                                                        borderRadius: window.innerWidth < 768 ? '8px' : '12px'
                                                    }}
                                                />
                                                <RefreshCw
                                                    size={window.innerWidth < 768 ? 14 : 16}
                                                    style={{
                                                        position: 'absolute',
                                                        left: window.innerWidth < 768 ? '12px' : '16px',
                                                        top: '50%',
                                                        transform: 'translateY(-50%)',
                                                        color: apiKeys.gemini.secondary ? '#00ff88' : '#71717a'
                                                    }}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div style={{
                                    marginBottom: '24px',
                                    padding: window.innerWidth < 768 ? '16px' : '24px',
                                    background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(6, 182, 212, 0.05) 100%)',
                                    borderRadius: window.innerWidth < 768 ? '8px' : '16px',
                                    border: '1px solid rgba(16, 185, 129, 0.2)',
                                    position: 'relative',
                                    overflow: 'hidden'
                                }}>
                                    <div style={{
                                        position: 'absolute',
                                        top: 0,
                                        left: 0,
                                        right: 0,
                                        height: '2px',
                                        background: 'linear-gradient(90deg, #10b981, #06b6d4)',
                                        opacity: 0.6
                                    }}></div>

                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                                        <div style={{
                                            width: window.innerWidth < 768 ? '32px' : '40px',
                                            height: window.innerWidth < 768 ? '32px' : '40px',
                                            background: 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)',
                                            borderRadius: '8px',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center'
                                        }}>
                                            <Zap size={window.innerWidth < 768 ? 16 : 20} color="white" />
                                        </div>
                                        <div>
                                            <h4 style={{
                                                fontSize: window.innerWidth < 768 ? '14px' : '18px',
                                                fontWeight: '700',
                                                color: '#ffffff',
                                                margin: 0
                                            }}>
                                                OpenAI (Optional)
                                            </h4>
                                            <p style={{
                                                fontSize: window.innerWidth < 768 ? '11px' : '14px',
                                                color: '#a1a1aa',
                                                margin: 0
                                            }}>
                                                Enhanced parsing capabilities
                                            </p>
                                        </div>
                                    </div>

                                    <div style={{ maxWidth: window.innerWidth < 768 ? '100%' : '500px' }}>
                                        <label style={{
                                            ...styles.label,
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '6px',
                                            color: '#10b981'
                                        }}>
                                            <Activity size={12} />
                                            API Key
                                        </label>
                                        <div style={{ position: 'relative' }}>
                                            <input
                                                type="password"
                                                placeholder="sk-openai-key..."
                                                value={apiKeys?.openai}
                                                onChange={(e) => updateOpenaiKey(e.target.value)}
                                                style={{
                                                    ...styles.input,
                                                    paddingLeft: window.innerWidth < 768 ? '36px' : '48px',
                                                    background: 'rgba(0, 0, 0, 0.4)',
                                                    border: '1px solid rgba(16, 185, 129, 0.3)',
                                                    borderRadius: window.innerWidth < 768 ? '8px' : '12px'
                                                }}
                                            />
                                            <Activity
                                                size={window.innerWidth < 768 ? 14 : 16}
                                                style={{
                                                    position: 'absolute',
                                                    left: window.innerWidth < 768 ? '12px' : '16px',
                                                    top: '50%',
                                                    transform: 'translateY(-50%)',
                                                    color: apiKeys.openai ? '#00ff88' : '#71717a'
                                                }}
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/* Privacy Notice */}
                                <div style={{
                                    marginBottom: '24px',
                                    padding: window.innerWidth < 768 ? '12px' : '16px',
                                    background: 'rgba(34, 197, 94, 0.05)',
                                    borderRadius: window.innerWidth < 768 ? '6px' : '8px',
                                    border: '1px solid rgba(34, 197, 94, 0.2)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '12px'
                                }}>
                                    <div style={{
                                        background: 'rgba(34, 197, 94, 0.2)',
                                        borderRadius: '50%',
                                        padding: '6px',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        minWidth: '32px',
                                        height: '32px'
                                    }}>
                                        <span style={{ fontSize: '14px' }}>🔒</span>
                                    </div>
                                    <div>
                                        <p style={{
                                            color: 'rgba(255, 255, 255, 0.9)',
                                            fontSize: window.innerWidth < 768 ? '12px' : '14px',
                                            margin: 0,
                                            fontWeight: '500'
                                        }}>
                                            <strong>Privacy Protected:</strong> Your API keys are not stored anywhere and will be removed on browser reload
                                        </p>
                                    </div>
                                </div>

                                <div style={{
                                    padding: window.innerWidth < 768 ? '16px' : '20px',
                                    background: 'rgba(255, 255, 255, 0.02)',
                                    borderRadius: window.innerWidth < 768 ? '8px' : '12px',
                                    border: '1px solid rgba(255, 255, 255, 0.1)'
                                }}>
                                    <h4 style={{
                                        fontSize: window.innerWidth < 768 ? '14px' : '16px',
                                        fontWeight: '600',
                                        color: '#e4e4e7',
                                        marginBottom: '12px'
                                    }}>
                                        Configuration Status
                                    </h4>
                                    <div style={{
                                        display: 'flex',
                                        flexDirection: window.innerWidth < 768 ? 'column' : 'row',
                                        gap: window.innerWidth < 768 ? '8px' : '24px',
                                        flexWrap: 'wrap'
                                    }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                            <div style={{
                                                width: '6px',
                                                height: '6px',
                                                borderRadius: '50%',
                                                backgroundColor: apiKeys.gemini.primary ? '#00ff88' : '#71717a'
                                            }}></div>
                                            <span style={{
                                                fontSize: window.innerWidth < 768 ? '12px' : '14px',
                                                color: '#a1a1aa'
                                            }}>
                                                Gemini Primary
                                            </span>
                                        </div>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                            <div style={{
                                                width: '6px',
                                                height: '6px',
                                                borderRadius: '50%',
                                                backgroundColor: apiKeys.gemini.secondary ? '#00ff88' : '#71717a'
                                            }}></div>
                                            <span style={{
                                                fontSize: window.innerWidth < 768 ? '12px' : '14px',
                                                color: '#a1a1aa'
                                            }}>
                                                Gemini Secondary
                                            </span>
                                        </div>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                            <div style={{
                                                width: '6px',
                                                height: '6px',
                                                borderRadius: '50%',
                                                backgroundColor: apiKeys.openai ? '#00ff88' : '#71717a'
                                            }}></div>
                                            <span style={{
                                                fontSize: window.innerWidth < 768 ? '12px' : '14px',
                                                color: '#a1a1aa'
                                            }}>
                                                OpenAI
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Auto-save notice */}
                    <div style={{
                        marginTop: '24px',
                        padding: '12px 16px',
                        background: 'rgba(0, 212, 255, 0.05)',
                        borderRadius: '8px',
                        border: '1px solid rgba(0, 212, 255, 0.1)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                    }}>
                        <div style={{
                            width: '20px',
                            height: '20px',
                            background: 'linear-gradient(135deg, #00d4ff, #7c3aed)',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            flexShrink: 0
                        }}>
                            <CheckCircle size={12} color="white" />
                        </div>
                        <div style={{ flex: 1 }}>
                            <p style={{
                                margin: 0,
                                fontSize: window.innerWidth < 768 ? '11px' : '13px',
                                color: 'rgba(255, 255, 255, 0.8)',
                                lineHeight: '1.4'
                            }}>
                                <strong style={{ color: '#00d4ff' }}>Auto-Save:</strong> All configuration changes are applied instantly and persist during your session. Simply close when you're done configuring.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ConfigurationModal;