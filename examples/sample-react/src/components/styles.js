const styles = {
    brandSection: {
        flex: 1,
        display: 'flex',
        alignItems: 'center',
    },
    logoBrandContainer: {
        display: 'flex',
        alignItems: 'center',
        gap: '20px',
    },
    brandInfo: {
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
    },
    title: {
        fontSize: '32px',
        fontWeight: '700',
        background: 'linear-gradient(135deg, #ffffff 0%, #00d4ff 100%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        margin: 0,
        letterSpacing: '-0.02em',
        lineHeight: '1.1',
        display: 'flex',
        alignItems: 'baseline',
        gap: '5px',
    },
    titleSub: {
        fontSize: '14px',
        fontWeight: '600',
        color: '#94a3b8',
        textTransform: 'uppercase',
        letterSpacing: '0.12em',
        WebkitBackgroundClip: 'unset',
        WebkitTextFillColor: 'unset',
        opacity: 1,
    },
    subtitle: {
        color: '#94a3b8',
        fontSize: '15px',
        margin: 0,
        fontWeight: '500',
        letterSpacing: '0.025em',
    },
    logo: {
        width: '70px',
        height: '70px',
        flexShrink: 0,
    },
    container: {
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '24px',
        backgroundColor: '#0a0a0a',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", Roboto, sans-serif',
        minHeight: '100vh',
        color: '#ffffff',
        width: '100%',
        boxSizing: 'border-box'
    },
    header: {
        marginBottom: '32px',
        background: 'linear-gradient(135deg, #1e1e2e 0%, #2d2d3a 100%)',
        borderRadius: '16px',
        padding: '32px',
        border: '1px solid #333344',
        position: 'relative',
        overflow: 'hidden'
    },
    headerGlow: {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '1px',
        background: 'linear-gradient(90deg, transparent, #00d4ff, transparent)',
        opacity: 0.6
    },

    statusContainer: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start'
    },
    statusIndicator: {
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        padding: '12px 20px',
        background: 'rgba(0, 212, 255, 0.1)',
        borderRadius: '50px',
        border: '1px solid rgba(0, 212, 255, 0.2)',
        backdropFilter: 'blur(10px)'
    },
    statusDot: {
        width: '8px',
        height: '8px',
        borderRadius: '50%',
        flexShrink: 0,
        boxShadow: '0 0 10px currentColor'
    },
    statusConnected: { backgroundColor: '#00ff88', color: '#00ff88' },
    statusDisconnected: { backgroundColor: '#ff4757', color: '#ff4757' },
    statusChecking: { backgroundColor: '#ffa502', color: '#ffa502' },
    errorAlert: {
        marginBottom: '24px',
        background: 'linear-gradient(135deg, #2d1b1b 0%, #3d2222 100%)',
        border: '1px solid #ff4757',
        borderRadius: '12px',
        padding: '20px',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '16px'
    },
    querySection: {
        marginBottom: '32px',
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        borderRadius: '16px',
        padding: '32px',
        border: '1px solid #333344',
        position: 'relative'
    },
    queryGlow: {
        position: 'absolute',
        top: '-1px',
        left: '-1px',
        right: '-1px',
        bottom: '-1px',
        background: 'linear-gradient(135deg, #00d4ff, #7c3aed, #00d4ff)',
        borderRadius: '16px',
        opacity: 0,
        transition: 'opacity 0.3s ease',
        zIndex: -1
    },
    label: {
        display: 'block',
        fontSize: '14px',
        fontWeight: '600',
        color: '#e4e4e7',
        marginBottom: '12px',
        letterSpacing: '0.02em',
        textTransform: 'uppercase'
    },
    inputGroup: {
        display: 'flex',
        gap: '16px',
        alignItems: 'stretch'
    },
    input: {
        flex: 1,
        padding: '16px 20px',
        background: 'rgba(255, 255, 255, 0.05)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '12px',
        fontSize: '16px',
        outline: 'none',
        color: '#ffffff',
        transition: 'all 0.3s ease',
        backdropFilter: 'blur(10px)'
    },
    inputFocus: {
        borderColor: '#00d4ff',
        boxShadow: '0 0 20px rgba(0, 212, 255, 0.3)'
    },
    button: {
        padding: '16px 24px',
        background: 'linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%)',
        color: 'white',
        border: 'none',
        borderRadius: '12px',
        fontSize: '15px',
        fontWeight: '600',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        transition: 'all 0.3s ease',
        position: 'relative',
        overflow: 'hidden'
    },
    buttonHover: {
        transform: 'translateY(-2px)',
        boxShadow: '0 10px 25px rgba(0, 212, 255, 0.4)'
    },
    buttonDisabled: {
        opacity: 0.5,
        cursor: 'not-allowed',
        transform: 'none'
    },
    buttonSecondary: {
        background: 'linear-gradient(135deg, #374151 0%, #4b5563 100%)'
    },
    buttonSuccess: {
        background: 'linear-gradient(135deg, #059669 0%, #10b981 100%)'
    },
    buttonDanger: {
        background: 'linear-gradient(135deg, #dc2626 0%, #ef4444 100%)'
    },
    configButton: {
        padding: '12px 20px',
        background: 'linear-gradient(135deg, #374151 0%, #4b5563 100%)',
        color: 'white',
        border: 'none',
        borderRadius: '12px',
        fontSize: '14px',
        fontWeight: '600',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        transition: 'all 0.3s ease',
        marginBottom: '24px'
    },
    modalOverlay: {
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.9)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 10000,
        backdropFilter: 'blur(15px)',
        overflow: 'auto',
        '-webkit-overflow-scrolling': 'touch'
    },
    modalContent: {
        background: 'linear-gradient(135deg, #1e1e2e 0%, #2d2d3a 100%)',
        borderRadius: '16px',
        border: '1px solid #333344',
        width: '90vw',
        maxWidth: '1200px',
        maxHeight: '90vh',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.6)'
    },
    modalHeader: {
        padding: '24px 32px',
        borderBottom: '1px solid #333344',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #2d2d3a 0%, #1e1e2e 100%)',
        flexShrink: 0,
        '@media (max-width: 768px)': {
            padding: '16px 20px',
            gap: '12px',
            minHeight: '60px'
        }
    },
    modalBody: {
        padding: '32px',
        overflow: 'auto',
        flex: 1,
        '-webkit-overflow-scrolling': 'touch',
        overscrollBehavior: 'contain'
    },
    tabs: {
        display: 'flex',
        gap: '4px',
        marginBottom: '24px',
        background: 'rgba(255, 255, 255, 0.05)',
        padding: '8px',
        borderRadius: '12px',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(10px)'
    },
    tab: {
        padding: '12px 20px',
        border: 'none',
        borderRadius: '8px',
        fontSize: '14px',
        fontWeight: '600',
        cursor: 'pointer',
        transition: 'all 0.3s ease',
        flex: 1,
        textAlign: 'center',
        background: 'transparent',
        color: '#a1a1aa',
        whiteSpace: 'nowrap',
        overflow: 'visible',
        textOverflow: 'unset'
    },
    tabActive: {
        background: 'linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%)',
        color: '#ffffff',
        boxShadow: '0 4px 12px rgba(0, 212, 255, 0.3)'
    },
    configActions: {
        display: 'flex',
        gap: '12px',
        marginBottom: '24px',
        flexWrap: 'wrap'
    },
    smallButton: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
        padding: '10px 16px',
        fontSize: '14px',
        border: 'none',
        borderRadius: '8px',
        cursor: 'pointer',
        fontWeight: '500',
        transition: 'all 0.3s ease',
        background: 'rgba(255, 255, 255, 0.1)',
        color: '#ffffff',
        backdropFilter: 'blur(10px)'
    },
    configPanel: {
        background: 'linear-gradient(135deg, #1e1e2e 0%, #2d2d3a 100%)',
        borderRadius: '16px',
        padding: '32px',
        marginBottom: '32px',
        border: '1px solid #333344',
        backdropFilter: 'blur(20px)'
    },
    sectionTitle: {
        fontSize: '20px',
        fontWeight: '700',
        color: '#ffffff',
        marginBottom: '24px',
        letterSpacing: '-0.02em',
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
    },
    grid: {
        display: 'grid',
        gap: '24px'
    },
    gridCols2: {
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))'
    },
    gridCols3: {
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))'
    },
    checkbox: {
        marginRight: '12px',
        width: '18px',
        height: '18px',
        accentColor: '#00d4ff'
    },
    textarea: {
        width: '100%',
        padding: '16px',
        background: 'rgba(0, 0, 0, 0.3)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '12px',
        fontSize: '13px',
        fontFamily: '"JetBrains Mono", "Fira Code", monospace',
        resize: 'vertical',
        outline: 'none',
        color: '#ffffff',
        overflow: 'hidden',
        transition: 'border-color 0.3s ease',
        lineHeight: '1.6',
        boxSizing: 'border-box'
    },
    select: {
        width: '100%',
        padding: '12px 16px',
        background: 'rgba(255, 255, 255, 0.05)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '8px',
        outline: 'none',
        fontSize: '14px',
        fontWeight: '500',
        cursor: 'pointer',
        color: 'white',
        transition: 'border-color 0.3s ease'
    },
    option: {
        background: '#1a1a1a',
        color: 'white'
    },
    slider: {
        width: '100%',
        marginTop: '12px',
        height: '6px',
        accentColor: '#00d4ff'
    },
    card: {
        background: 'rgba(255, 255, 255, 0.03)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '12px',
        padding: '20px',
        transition: 'all 0.3s ease',
        backdropFilter: 'blur(10px)'
    },
    cardHover: {
        background: 'rgba(255, 255, 255, 0.05)',
        borderColor: 'rgba(0, 212, 255, 0.3)',
        transform: 'translateY(-2px)'
    },
    cardGrid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '20px'
    },
    results: {
        background: 'linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%)',
        borderRadius: '16px',
        padding: '32px',
        border: '1px solid #333344',
        position: 'relative'
    },
    metricsCard: {
        background: 'linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%)',
        color: 'white',
        border: 'none'
    },
    citationItem: {
        fontSize: '13px',
        padding: '12px 16px',
        background: 'rgba(0, 212, 255, 0.1)',
        borderRadius: '8px',
        border: '1px solid rgba(0, 212, 255, 0.2)',
        borderLeft: '4px solid #00d4ff',
        wordBreak: 'break-all'
    },
    schemaKeyRow: {
        display: 'grid',
        gridTemplateColumns: '1fr 140px 2fr 100px 60px',
        gap: '16px',
        padding: '20px',
        background: 'rgba(255, 255, 255, 0.02)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '12px',
        alignItems: 'center'
    },
    schemaKeyRowMobile: {
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        padding: '12px',
        background: 'rgba(255, 255, 255, 0.02)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '8px',
        marginBottom: '12px'
    },
    schemaKeyInput: {
        width: '100%',
        boxSizing: 'border-box'
    },
    schemaKeyLabel: {
        fontSize: '11px',
        fontWeight: '600',
        color: '#a1a1aa',
        marginBottom: '4px',
        textTransform: 'uppercase',
        letterSpacing: '0.5px'
    }
};

export default styles;