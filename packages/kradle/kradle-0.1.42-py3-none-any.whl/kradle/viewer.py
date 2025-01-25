def display_viewer():
    """Display the Kradle viewer optimized for Jupyter Notebook with maximum rendering performance."""
    from IPython.display import display, HTML
    
    viewer_html = """
    <div style="margin: 20px 0 40px 0; padding: 0;">
        <div style="height: 400px; width: 700px; background: #000000; font-family: system-ui, -apple-system, sans-serif; transform: translate3d(0,0,0); will-change: transform;">
            <!-- Header -->
            <div style="padding: 0 1.5rem; display: flex; align-items: center; justify-content: space-between; height: 56px; background: rgba(255,255,255,0.03); backdrop-filter: blur(8px); transform: translate3d(0,0,0);">
                <span style="color: white; font-size: 1.25rem; font-weight: 500;">Kradle</span>
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span id="view-label" style="color: rgba(255,255,255,0.7); font-size: 0.875rem;">First Person</span>
                    <label class="toggle" style="position: relative; display: inline-block; width: 48px; height: 28px; margin: 0;">
                        <input type="checkbox" id="view-toggle" style="opacity: 0; width: 0; height: 0; margin: 0;">
                        <span style="position: absolute; cursor: pointer; inset: 0; background: rgba(255,255,255,0.1); border-radius: 34px; transition: transform 0.2s ease-out;"></span>
                        <span style="position: absolute; content: ''; height: 20px; width: 20px; left: 4px; bottom: 4px; background: white; border-radius: 50%; transition: transform 0.2s ease-out;">
                        </span>
                    </label>
                </div>
            </div>

            <!-- Loading State -->
            <div id="loading-message" style="color: white; text-align: center; padding-top: 120px;">
                <div style="font-size: 1rem; animation: pulse 2s infinite ease-in-out;">
                    Initializing Kradle environment
                </div>
                <div style="color: rgba(255,255,255,0.5); font-size: 0.875rem; margin-top: 8px;">
                    This takes 1-2 minutes
                </div>
            </div>
            
            <!-- Viewer -->
            <iframe id="view-frame"
                    style="width: 100%; height: calc(100% - 56px); border: none; display: none; opacity: 0; 
                           transform: translate3d(0,0,0);
                           -webkit-transform: translate3d(0,0,0);
                           -webkit-backface-visibility: hidden;
                           -webkit-perspective: 1000;
                           backface-visibility: hidden;
                           perspective: 1000;
                           transition: opacity 0.3s ease-out;">
            </iframe>

            <style>
                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.5; }
                    100% { opacity: 1; }
                }
                
                .toggle input:checked + span {
                    background: #2563eb;
                }
                
                .toggle input:checked + span + span {
                    transform: translateX(20px);
                }
                
                .toggle span:nth-of-type(1):hover {
                    background: rgba(255,255,255,0.15);
                }
                
                .toggle input:checked + span:hover {
                    background: #1d4ed8;
                }
                
                #view-frame.visible {
                    opacity: 1;
                }
            </style>

            <script>
                (() => {
                    const toggle = document.getElementById('view-toggle');
                    const label = document.getElementById('view-label');
                    const frame = document.getElementById('view-frame');
                    const loadingMsg = document.getElementById('loading-message');
                    let attempts = 0;
                    const maxAttempts = 120;
                    let checkTimeout;

                    const switchView = (url, isThirdPerson) => {
                        requestAnimationFrame(() => {
                            frame.style.opacity = '0';
                            
                            // Use setTimeout to ensure opacity transition completes
                            setTimeout(() => {
                                frame.src = url;
                                label.textContent = isThirdPerson ? 'Third Person' : 'First Person';
                                
                                // Wait for next frame to start fade in
                                requestAnimationFrame(() => {
                                    frame.style.opacity = '1';
                                });
                            }, 300);
                        });
                    };
                    
                    const checkServer = () => {
                        if (attempts >= maxAttempts) {
                            loadingMsg.innerHTML = `
                                <div style="color: #ef4444;">Connection failed</div>
                                <div style="color: rgba(255,255,255,0.5); font-size: 0.875rem; margin-top: 8px;">
                                    Please try again
                                </div>`;
                            return;
                        }
                        
                        fetch('http://localhost:4000', { 
                            method: 'GET',
                            mode: 'no-cors',
                            cache: 'no-cache'
                        })
                        .then(() => {
                            loadingMsg.style.display = 'none';
                            frame.style.display = 'block';
                            
                            requestAnimationFrame(() => {
                                frame.style.opacity = '1';
                                switchView('http://localhost:4000', false);
                            });
                        })
                        .catch(() => {
                            attempts++;
                            checkTimeout = setTimeout(checkServer, 1000);
                        });
                    };
                    
                    // Debounce the toggle to prevent rapid switching
                    const debounce = (func, wait) => {
                        let timeout;
                        return (...args) => {
                            clearTimeout(timeout);
                            timeout = setTimeout(() => func.apply(this, args), wait);
                        };
                    };
                    
                    toggle.onchange = debounce(() => {
                        switchView(
                            toggle.checked ? 'http://localhost:4001' : 'http://localhost:4000',
                            toggle.checked
                        );
                    }, 150);
                    
                    checkServer();
                    
                    // Cleanup function
                    window.addEventListener('beforeunload', () => {
                        clearTimeout(checkTimeout);
                    });
                })();
            </script>
        </div>
    </div>
    """
    
    display(HTML(viewer_html))