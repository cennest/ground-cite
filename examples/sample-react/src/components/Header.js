import React, { useState } from 'react';
import { Brain, Settings, Menu, X } from 'lucide-react';
import styles from './styles';
import './Responsive.css';

const Header = ({
    backendStatus,
    onConfigClick,
    error,
    setError,
    needsConfiguration = false
}) => {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    return (
        <header className="header main-container">
            <div className="header-inner" style={styles.header}>
                <div className="header-glow" style={styles.headerGlow}></div>
                <div className="status-container" style={{
                    ...styles.statusContainer,
                    alignItems: 'center'
                }}>
                    <div className="brand-section" style={styles.brandSection}>
                        <div className="logo-brand-container" style={styles.logoBrandContainer}>
                            <img
                                style={styles.logo}
                                src="/logo.png"
                                alt="GroundCite Logo"
                            />
                            <div className="brand-info" style={styles.brandInfo}>
                                <h1 className="title" style={styles.title}>
                                    <span style={styles.titleSub}>Playground for</span>
                                    GroundCite
                                </h1>
                                <p className="subtitle" style={styles.subtitle}>
                                    Advanced Gemini-powered search with better grounding and citation control
                                </p>
                            </div>
                        </div>
                    </div>

                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '20px'
                    }}>
                        <div className="status-indicator" style={styles.statusIndicator}>
                            <div className="status-dot" style={{
                                ...styles.statusDot,
                                ...(backendStatus === 'connected' ? styles.statusConnected :
                                    backendStatus === 'disconnected' ? styles.statusDisconnected :
                                        styles.statusChecking)
                            }}></div>
                            <span className="status-text" style={{ fontSize: '14px', fontWeight: '600' }}>
                                AI {backendStatus === 'connected' ? 'Online' :
                                    backendStatus === 'disconnected' ? 'Offline' : 'Connecting...'}
                            </span>
                        </div>

                        {/* Quick Links */}
                        <div className="quick-links" style={{
                            display: 'flex',
                            gap: '12px',
                            alignItems: 'center'
                        }}>
                            <a
                                href="https://www.cennest.com/category/groundcite/"
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '6px',
                                    padding: '6px 12px',
                                    background: 'rgba(0, 212, 255, 0.1)',
                                    color: '#00d4ff',
                                    textDecoration: 'none',
                                    borderRadius: '6px',
                                    fontSize: '12px',
                                    fontWeight: '600',
                                    border: '1px solid rgba(0, 212, 255, 0.2)',
                                    transition: 'all 0.3s ease'
                                }}
                                onMouseEnter={(e) => {
                                    e.target.style.background = 'rgba(0, 212, 255, 0.2)';
                                    e.target.style.borderColor = 'rgba(0, 212, 255, 0.4)';
                                }}
                                onMouseLeave={(e) => {
                                    e.target.style.background = 'rgba(0, 212, 255, 0.1)';
                                    e.target.style.borderColor = 'rgba(0, 212, 255, 0.2)';
                                }}
                            >
                                📚 Why GroundCite
                            </a>
                            <a
                                href="https://github.com/cennest/ground-cite"
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '6px',
                                    padding: '6px 12px',
                                    background: 'rgba(255, 255, 255, 0.05)',
                                    color: '#a1a1aa',
                                    textDecoration: 'none',
                                    borderRadius: '6px',
                                    fontSize: '12px',
                                    fontWeight: '600',
                                    border: '1px solid rgba(255, 255, 255, 0.1)',
                                    transition: 'all 0.3s ease'
                                }}
                                onMouseEnter={(e) => {
                                    e.target.style.background = 'rgba(255, 255, 255, 0.1)';
                                    e.target.style.color = '#ffffff';
                                    e.target.style.borderColor = 'rgba(255, 255, 255, 0.2)';
                                }}
                                onMouseLeave={(e) => {
                                    e.target.style.background = 'rgba(255, 255, 255, 0.05)';
                                    e.target.style.color = '#a1a1aa';
                                    e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                                }}
                            >
                                ⭐ Fork Repo
                            </a>
                        </div>
                    </div>
                </div>
            </div>

            {/* Error Display */}
            {error && (
                <div className="error-alert" style={styles.errorAlert}>
                    <div className="error-alert-inner" style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', flex: 1 }}>
                        <div className="error-icon" style={{
                            color: '#ff4757',
                            fontSize: '18px',
                            minWidth: '20px',
                            marginTop: '2px'
                        }}>
                            ⚠️
                        </div>
                        <div className="error-content" style={{ flex: 1 }}>
                            <h4 className="error-title" style={{
                                color: '#ff6b7a',
                                fontSize: '14px',
                                fontWeight: '600',
                                margin: '0 0 4px 0'
                            }}>
                                System Alert
                            </h4>
                            <p className="error-message" style={{
                                color: '#ff8a94',
                                fontSize: '14px',
                                margin: '4px 0 0 0',
                                lineHeight: '1.4'
                            }}>
                                {error}
                            </p>
                        </div>
                    </div>
                    <button
                        className="error-close"
                        onClick={() => setError(null)}
                        style={{
                            background: 'none',
                            border: 'none',
                            color: '#ff4757',
                            cursor: 'pointer',
                            fontSize: '18px',
                            padding: '4px',
                            borderRadius: '4px',
                            minWidth: '28px',
                            height: '28px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}
                    >
                        ×
                    </button>
                </div>
            )}

            {/* Configuration Button */}
            <button
                className="config-button"
                onClick={onConfigClick}
                style={{
                    ...styles.configButton,
                    ...(needsConfiguration ? {
                        background: 'linear-gradient(135deg, #ffc107, #ff9800)',
                        color: '#000',
                        fontWeight: '700',
                        animation: 'pulse 2s ease-in-out infinite',
                        boxShadow: '0 4px 20px rgba(255, 193, 7, 0.4)'
                    } : {})
                }}
            >
                <Settings size={14} />
                {needsConfiguration ? 'Setup Required - Configure AI Models' : 'Configure AI Models'}
            </button>
        </header>
    );
};

export default Header;
