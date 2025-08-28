import React from 'react';
import { Brain, Zap, Send, RefreshCw } from 'lucide-react';
import styles from './styles';
import './Responsive.css';

const QueryInput = ({
    query,
    setQuery,
    systemInstruction,
    setSystemInstruction,
    isLoading,
    focusedInput,
    setFocusedInput,
    onAnalyze,
    hasApiKeys = true
}) => {
    return (
        <div className="query-input main-container">
            <div className="query-section" style={styles.querySection}>
                <div className="query-glow" style={{
                    ...styles.queryGlow,
                    opacity: focusedInput ? 0.7 : 0
                }}></div>

                <div className="query-input-block" style={{ marginBottom: '24px' }}>
                    <label className="label" style={styles.label}>
                        <Brain size={14} style={{ display: 'inline', marginRight: '6px' }} />
                        System Instruction (Optional)
                    </label>
                    <textarea
                        value={systemInstruction}
                        onChange={(e) => setSystemInstruction(e.target.value)}
                        placeholder="Provide context or specific instructions for the AI..."
                        rows={3}
                        style={{
                            ...styles.textarea,
                            marginBottom: 0,
                            background: 'rgba(255, 255, 255, 0.05)',
                            border: '1px solid rgba(255, 255, 255, 0.1)'
                        }}
                    />
                </div>

                <label className="label" style={styles.label}>
                    <Zap size={14} style={{ display: 'inline', marginRight: '6px' }} />
                    Query Input
                </label>
                <div className="input-group" style={styles.inputGroup}>
                    <input className="input"
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onFocus={() => setFocusedInput(true)}
                        onBlur={() => setFocusedInput(false)}
                        placeholder={hasApiKeys ? "Ask me anything..." : "Configure API keys first to start analyzing..."}
                        disabled={!hasApiKeys}
                        style={{
                            ...styles.input,
                            ...(focusedInput ? styles.inputFocus : {}),
                            ...((!hasApiKeys) ? {
                                opacity: 0.6,
                                cursor: 'not-allowed',
                                background: 'rgba(255, 255, 255, 0.03)'
                            } : {})
                        }}
                        onKeyPress={(e) => {
                            if (e.key === 'Enter' && query && !isLoading && hasApiKeys) {
                                onAnalyze();
                            }
                        }}
                    />
                    <button className="button"
                        onClick={onAnalyze}
                        disabled={!query || isLoading || !hasApiKeys}
                        style={{
                            ...styles.button,
                            ...((!query || isLoading || !hasApiKeys) ? styles.buttonDisabled : {}),
                            ...(isLoading ? {
                                background: 'linear-gradient(-45deg, #00d4ff, #7c3aed, #00d4ff, #7c3aed)',
                                backgroundSize: '400% 400%',
                                animation: 'shimmer 2s ease-in-out infinite, pulse 1.5s ease-in-out infinite',
                                cursor: 'not-allowed',
                                boxShadow: '0 0 20px rgba(0, 212, 255, 0.4)',
                                transform: 'none'
                            } : {}),
                            ...(!hasApiKeys ? {
                                opacity: 0.5,
                                cursor: 'not-allowed'
                            } : {})
                        }}
                        onMouseEnter={(e) => {
                            if (!e.target.disabled && !isLoading && hasApiKeys) {
                                Object.assign(e.target.style, styles.buttonHover);
                            }
                        }}
                        onMouseLeave={(e) => {
                            if (!isLoading && hasApiKeys) {
                                Object.assign(e.target.style, styles.button);
                            }
                        }}
                    >
                        {isLoading ? (
                            <RefreshCw
                                size={16}
                                style={{
                                    animation: 'spin 0.8s linear infinite',
                                    filter: 'drop-shadow(0 0 4px rgba(255, 255, 255, 0.8))',
                                    color: '#ffffff'
                                }}
                            />
                        ) : (
                            <Send size={16} />
                        )}
                        {isLoading ? 'Processing...' : 'Analyze'}
                    </button>
                </div>
            </div>
        </div >
    );
};

export default QueryInput;