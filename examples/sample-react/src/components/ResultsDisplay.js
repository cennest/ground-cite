import React from 'react';
import ReactMarkdown from "react-markdown";
import { CheckCircle } from 'lucide-react';
import styles from './styles';
import './Responsive.css';

const ResultsDisplay = ({ results }) => {
    if (!results) return null;

    const formatObjectAsMarkdown = (obj, level = 0) => {
        let markdown = '';
        const indent = '  '.repeat(level);

        for (const [key, value] of Object.entries(obj)) {
            if (Array.isArray(value)) {
                markdown += `${indent}**${key}:**\n`;
                value.forEach(item => {
                    markdown += `${indent}- ${item}\n`;
                });
                markdown += '\n';
            } else if (typeof value === 'object' && value !== null) {
                markdown += `${indent}**${key}:**\n`;
                markdown += formatObjectAsMarkdown(value, level + 1);
            } else {
                markdown += `${indent}**${key}:** ${value}\n\n`;
            }
        }

        return markdown;
    };

    const getContentMarkdown = () => {
        const content = results?.final_content?.content;

        if (!content) {
            return "No content available";
        }

        if (typeof content === "string") {
            return content;
        }

        return formatObjectAsMarkdown(content);
    };

    return (
        <div className="results main-container">
            <div style={styles.results}>
                <h3 style={{
                    ...styles.sectionTitle,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px'
                }}>
                    <CheckCircle size={24} color="#00ff88" />
                    AI Analysis Results
                </h3>

                <div style={{
                    ...styles.grid,
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: '20px',
                    marginBottom: '32px'
                }}>
                    <div style={{ ...styles.card, ...styles.metricsCard }}>
                        <h4 style={{
                            fontSize: '14px',
                            fontWeight: '500',
                            marginBottom: '6px',
                            opacity: 0.9
                        }}>
                            Processing Status
                        </h4>
                        <p style={{
                            fontSize: '20px',
                            fontWeight: '700',
                            margin: 0
                        }}>
                            {results.completed ? '✓ Complete' : '✗ Failed'}
                        </p>
                    </div>

                    <div style={styles.card}>
                        <h4 style={{
                            fontSize: '14px',
                            fontWeight: '500',
                            color: '#a1a1aa',
                            marginBottom: '6px'
                        }}>
                            Execution Time
                        </h4>
                        <p style={{
                            fontSize: '20px',
                            fontWeight: '700',
                            color: '#ffffff',
                            margin: 0
                        }}>
                            {results.execution_metrics?.execution_time_seconds ?
                                `${results.execution_metrics.execution_time_seconds.toFixed(3)}s` : 'N/A'}
                        </p>
                    </div>

                    <div style={styles.card}>
                        <h4 style={{
                            fontSize: '14px',
                            fontWeight: '500',
                            color: '#a1a1aa',
                            marginBottom: '6px'
                        }}>
                            Token Usage
                        </h4>
                        <p style={{
                            fontSize: '20px',
                            fontWeight: '700',
                            color: '#ffffff',
                            margin: 0
                        }}>
                            {results.execution_metrics?.token_usage ? (() => {
                                try {
                                    const tokenData = JSON.parse(results.execution_metrics.token_usage);
                                    let totalTokens = 0;

                                    // Sum tokens from all operations (search, validation, parse)
                                    Object.values(tokenData).forEach(operation => {
                                        if (operation && operation.total_tokens) {
                                            totalTokens += operation.total_tokens;
                                        }
                                    });

                                    return totalTokens > 0 ? totalTokens.toLocaleString() : 'N/A';
                                } catch (e) {
                                    return 'N/A';
                                }
                            })() : 'N/A'}
                        </p>
                    </div>

                    <div style={styles.card}>
                        <h4 style={{
                            fontSize: '13px',
                            fontWeight: '500',
                            color: '#a1a1aa',
                            marginBottom: '6px'
                        }}>
                            Session ID
                        </h4>
                        <p style={{
                            fontSize: '13px',
                            fontFamily: 'monospace',
                            color: '#e4e4e7',
                            margin: 0,
                            wordBreak: 'break-all',
                            background: 'rgba(0, 0, 0, 0.3)',
                            padding: '8px',
                            borderRadius: '4px'
                        }}>
                            {results.execution_metrics?.session_id || 'N/A'}
                        </p>
                    </div>
                </div>

                {results.final_content && (
                    <div style={{ ...styles.card, marginBottom: '20px' }}>
                        <h4 style={{
                            fontSize: '18px',
                            fontWeight: '600',
                            color: '#ffffff',
                            marginBottom: '12px'
                        }}>
                            AI Response
                        </h4>
                        <div style={{
                            fontSize: '15px',
                            lineHeight: '1.7',
                            color: '#e4e4e7',
                            background: 'rgba(0, 0, 0, 0.3)',
                            padding: '24px',
                            borderRadius: '12px',
                            border: '1px solid rgba(0, 212, 255, 0.2)',
                            overflow: 'auto',
                            overflowX: 'auto',
                        }}>
                            <ReactMarkdown
                                components={{
                                    a: ({ node, ...props }) => (
                                        <a
                                            {...props}
                                            style={{ color: '#00d4ff', textDecoration: 'underline' }}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                        />
                                    ),
                                }}
                            >
                                {getContentMarkdown()}
                            </ReactMarkdown>
                        </div>
                    </div>
                )}

                {results.final_content?.citations && (
                    <div style={{ ...styles.card, marginBottom: '20px' }}>
                        <h4 style={{
                            fontSize: '18px',
                            fontWeight: '600',
                            color: '#ffffff',
                            marginBottom: '12px'
                        }}>
                            Sources ({results.final_content.citations.length})
                        </h4>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            {results.final_content.citations.map((citation, index) => (
                                <div key={index} style={styles.citationItem}>
                                    <span style={{
                                        fontWeight: '600',
                                        color: '#ffffff',
                                        fontSize: '13px'
                                    }}>
                                        Source {citation.chunk_index + 1}:
                                    </span>
                                    <a
                                        href={citation.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        style={{
                                            color: '#00d4ff',
                                            textDecoration: 'underline',
                                            marginLeft: '6px',
                                            fontSize: '12px',
                                            wordBreak: 'break-all'
                                        }}
                                    >
                                        {citation.url || citation.original_link}
                                    </a>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                <details style={styles.card}>
                    <summary style={{
                        cursor: 'pointer',
                        fontSize: '16px',
                        fontWeight: '600',
                        color: '#e4e4e7',
                        marginBottom: '12px'
                    }}>
                        Raw Data
                    </summary>
                    <pre style={{
                        fontSize: '11px',
                        color: '#a1a1aa',
                        overflowX: 'auto',
                        background: 'rgba(0, 0, 0, 0.5)',
                        padding: '20px',
                        borderRadius: '6px',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        maxHeight: '400px',
                        overflow: 'auto',
                        lineHeight: '1.4'
                    }}>
                        {JSON.stringify(results, null, 2)}
                    </pre>
                </details>
            </div>
        </div>
    );
};

export default ResultsDisplay;