// AI Assistant file loading
console.log('🤖 AI Assistant file is loading...');
console.log('🔍 Debug: Checking for any existing chatbot icons...');

class AIAssistant {
    constructor() {
        console.log('🤖 AI Assistant constructor called');
        this.isOpen = false;
        this.isResizing = false;
        this.currentChatId = null;
        this.messageOffset = 0;
        this.messagesPerPage = 25;
        this.hasMoreMessages = false;
        this.isLoadingMessages = false;
        this.chatHistory = [];
        this.init();
    }

    init() {
        console.log('Initializing AI Assistant...');
        this.createChatWidget();
        this.bindEvents();
        this.loadChatHistory();
        console.log('AI Assistant initialized successfully');
    }

    createChatWidget() {
        console.log('🔧 Creating AI chat widget...');
        
        // Remove any existing AI elements first
        $('.ai-button, .ai-pane').remove();
        
        // Create the floating AI button with chat icon and RGB animation
        this.chatButton = $(`
            <div class="ai-button" title="Ask AI Assistant">
                <img src="/assets/erpnext/images/unwatermark-Meta-Ai-unscreen.gif" 
                     width="32" height="32" 
                     style="position: relative; z-index: 1; border-radius: 4px;" 
                     alt="AI Assistant" 
                     onerror="console.error('Failed to load AI icon:', this.src)" />
            </div>
        `);

        // Create the right pane chat window - INITIALLY HIDDEN
        this.chatWindow = $(`
            <div class="ai-pane ai-closed">
                <div class="ai-pane-resizer"></div>
                <div class="ai-pane-content">
                    <div class="ai-header">
                        <div class="ai-header-title">
                            <img src="/assets/erpnext/images/unwatermark-Meta-Ai-unscreen.gif" 
                                 width="20" height="20" 
                                 style="position: relative; z-index: 1; border-radius: 4px;" 
                                 alt="AI Assistant" 
                                 onerror="console.error('Failed to load AI header icon:', this.src)" />
                            <span>OMEX AI</span>
                        </div>
                        <div class="ai-header-actions">
                            <button class="ai-new-chat" title="Start New Chat">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                </svg>
                            </button>
                            <button class="ai-close">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M18 6L6 18M6 6L18 18" stroke="#666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                </svg>
                            </button>
                        </div>
                    </div>
                    <div class="ai-messages">
                        <div class="ai-load-more" style="display: none;">
                            <button class="load-more-btn">Load More Messages</button>
                        </div>
                        <div class="ai-messages-content"></div>
                    </div>
                    <div class="ai-input-container">
                        <input type="text" class="ai-input" placeholder="Ask me anything..." />
                        <button class="ai-send">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z" fill="currentColor"/>
                            </svg>
                        </button>
                    </div>
                    <div class="ai-typing" style="display: none;">
                        <div class="typing-indicator">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                        AI is thinking...
                    </div>
                </div>
            </div>
        `);

        // Add CSS styles
        this.addStyles();

        // Append to body
        $('body').append(this.chatButton);
        $('body').append(this.chatWindow);
        
        // Force initial state
        this.isOpen = false;
        
        console.log('✅ AI button and window added to DOM');
    }

    addStyles() {
        console.log('🎨 Adding AI Assistant styles...');
        const styles = `
            <style>
                /* RGB Animation Keyframes */
                @keyframes rgbGradient {
                    0% { background-position: 0% 50%; }
                    25% { background-position: 100% 50%; }
                    50% { background-position: 100% 100%; }
                    75% { background-position: 0% 100%; }
                    100% { background-position: 0% 50%; }
                }

                /* AI Button - Smaller, rectangular, right-aligned */
                .ai-button {
                    position: fixed !important;
                    bottom: 80px !important;
                    right: 20px !important;
                    width: 50px !important;
                    height: 50px !important;
                    border-radius: 12px !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    cursor: pointer !important;
                    z-index: 99999 !important;
                    background: transparent !important;
                    overflow: visible !important;
                    transition: all 0.3s ease !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
                }

                .ai-button:hover {
                    transform: scale(1.1) translateY(-2px) !important;
                    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3) !important;
                }

                .ai-button img {
                    position: relative !important;
                    z-index: 1 !important;
                    transition: transform 0.2s ease !important;
                    border-radius: 4px !important;
                }

                .ai-button:hover img {
                    transform: scale(1.1) !important;
                }

                /* Right Pane */
                .ai-pane {
                    position: fixed !important;
                    top: 0 !important;
                    right: 0 !important;
                    height: 100vh !important;
                    width: 400px !important;
                    background: #fff !important;
                    box-shadow: -5px 0 25px rgba(0, 0, 0, 0.15) !important;
                    z-index: 100001 !important;
                    display: none;
                    transition: transform 0.3s ease !important;
                }

                .ai-pane.ai-open {
                    display: flex !important;
                }

                .ai-pane.ai-closed {
                    display: none !important;
                }

                .ai-pane-resizer {
                    position: absolute;
                    left: 0;
                    top: 0;
                    width: 5px;
                    height: 100%;
                    cursor: ew-resize;
                    background: transparent;
                    z-index: 10;
                }

                .ai-pane-resizer:hover {
                    background: rgba(139, 92, 246, 0.3) !important;
                }

                .ai-pane-content {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    height: 100%;
                }

                /* Header - WHITE BACKGROUND */
                .ai-header {
                    padding: 16px !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: space-between !important;
                    position: relative !important;
                    background: white !important;
                    border-bottom: 2px solid #e5e7eb !important;
                }

                .ai-header-title {
                    display: flex !important;
                    align-items: center !important;
                    gap: 8px !important;
                    color: #333 !important;
                    font-weight: 600 !important;
                    position: relative !important;
                    z-index: 1 !important;
                }

                .ai-header-actions {
                    display: flex !important;
                    align-items: center !important;
                    gap: 8px !important;
                }

                .ai-new-chat {
                    background: #f3f4f6 !important;
                    border: 2px solid #e5e7eb !important;
                    color: #666 !important;
                    cursor: pointer !important;
                    padding: 6px !important;
                    width: 32px !important;
                    height: 32px !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    border-radius: 50% !important;
                    transition: all 0.3s ease !important;
                    position: relative !important;
                    z-index: 10 !important;
                    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1) !important;
                }

                .ai-new-chat:hover {
                    background: #10b981 !important;
                    border-color: #059669 !important;
                    color: white !important;
                    transform: scale(1.1) rotate(90deg) !important;
                    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4) !important;
                }

                .ai-new-chat svg {
                    stroke: currentColor !important;
                }

                .ai-close {
                    background: #f3f4f6 !important;
                    border: 2px solid #e5e7eb !important;
                    color: #666 !important;
                    cursor: pointer !important;
                    padding: 6px !important;
                    width: 32px !important;
                    height: 32px !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    border-radius: 50% !important;
                    transition: all 0.3s ease !important;
                    position: relative !important;
                    z-index: 10 !important;
                    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1) !important;
                }

                .ai-close:hover {
                    background: #ef4444 !important;
                    border-color: #dc2626 !important;
                    color: white !important;
                    transform: scale(1.1) rotate(90deg) !important;
                    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4) !important;
                }

                .ai-close svg {
                    stroke: currentColor !important;
                }

                /* Messages Area */
                .ai-messages {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    background: #f8f9fa;
                    overflow: hidden;
                }

                .ai-messages-content {
                    flex: 1;
                    padding: 16px;
                    overflow-y: auto;
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                }

                .ai-load-more {
                    padding: 10px 16px;
                    text-align: center;
                    border-bottom: 1px solid #e5e7eb;
                    background: #f8f9fa;
                }

                .load-more-btn {
                    background: #8b5cf6 !important;
                    color: white !important;
                    border: none !important;
                    padding: 8px 16px !important;
                    border-radius: 6px !important;
                    cursor: pointer !important;
                    font-size: 12px !important;
                    transition: all 0.2s ease !important;
                }

                .load-more-btn:hover {
                    background: #7c3aed !important;
                    transform: translateY(-1px) !important;
                    box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3) !important;
                }

                .load-more-btn:disabled {
                    background: #d1d5db !important;
                    cursor: not-allowed !important;
                    transform: none !important;
                    box-shadow: none !important;
                }

                .ai-message, .user-message {
                    max-width: 85%;
                    padding: 12px 16px;
                    border-radius: 12px;
                    word-wrap: break-word;
                    line-height: 1.4;
                    position: relative;
                    z-index: 1;
                }

                .user-message {
                    background: linear-gradient(135deg, #8B5CF6, #EC4899) !important;
                    color: white !important;
                    align-self: flex-end;
                    margin-left: auto;
                    position: relative;
                    box-shadow: 0 2px 10px rgba(139, 92, 246, 0.3);
                }

                .ai-message {
                    background: white;
                    color: #333;
                    align-self: flex-start;
                    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
                    border-left: 3px solid #8B5CF6;
                }

                /* Input Area */
                .ai-input-container {
                    padding: 16px;
                    border-top: 1px solid #eee;
                    display: flex;
                    gap: 10px;
                    background: white;
                }

                .ai-input {
                    flex: 1;
                    padding: 12px 16px;
                    border: 2px solid #e5e7eb;
                    border-radius: 20px;
                    outline: none;
                    font-size: 14px;
                    background: #f8f9fa;
                    transition: all 0.3s ease;
                }

                .ai-input:focus {
                    border-color: #8B5CF6 !important;
                    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
                    background: white !important;
                }

                .ai-send {
                    background: #8B5CF6 !important;
                    border: none !important;
                    border-radius: 50% !important;
                    width: 44px !important;
                    height: 44px !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    cursor: pointer !important;
                    transition: all 0.3s ease !important;
                    position: relative !important;
                    overflow: hidden !important;
                    color: white !important;
                    box-shadow: 0 2px 10px rgba(139, 92, 246, 0.3) !important;
                }

                .ai-send::before {
                    content: '' !important;
                    position: absolute !important;
                    top: 0 !important;
                    left: 0 !important;
                    right: 0 !important;
                    bottom: 0 !important;
                    background: linear-gradient(
                        135deg,
                        #8B5CF6,
                        #EC4899,
                        #EF4444,
                        #3B82F6
                    ) !important;
                    background-size: 300% 300% !important;
                    animation: rgbGradient 8s ease infinite !important;
                    opacity: 0.9 !important;
                }

                .ai-send:hover {
                    transform: scale(1.1) !important;
                    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4) !important;
                }

                .ai-send svg {
                    position: relative !important;
                    z-index: 1 !important;
                }

                /* Typing Indicator */
                .ai-typing {
                    padding: 12px 16px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    background: white;
                    border-top: 1px solid #eee;
                    font-size: 12px;
                    color: #666;
                }

                .typing-indicator {
                    display: flex;
                    gap: 3px;
                }

                .typing-indicator span {
                    width: 6px;
                    height: 6px;
                    background: linear-gradient(135deg, #8B5CF6, #EC4899) !important;
                    border-radius: 50%;
                    animation: typing 1.4s infinite ease-in-out;
                }

                .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
                .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

                @keyframes typing {
                    0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
                    40% { transform: scale(1); opacity: 1; }
                }

                /* Action Buttons */
                .ai-actions {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 8px;
                    margin-top: 8px;
                }

                .action-button {
                    background: linear-gradient(135deg, #8B5CF6, #EC4899) !important;
                    color: white !important;
                    border: none !important;
                    padding: 8px 16px !important;
                    border-radius: 20px !important;
                    cursor: pointer !important;
                    font-size: 12px !important;
                    transition: all 0.3s ease !important;
                    white-space: nowrap !important;
                    box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3) !important;
                }

                .action-button:hover {
                    transform: translateY(-2px) !important;
                    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4) !important;
                }
            </style>
        `;

        // Remove existing styles if any
        $('style[data-ai-assistant]').remove();
        
        // Add new styles with identifier
        $(styles).attr('data-ai-assistant', 'true').appendTo('head');
        console.log('✅ AI Assistant styles added successfully');
    }

    bindEvents() {
        console.log('🔗 Binding AI Assistant events...');
        
        // Toggle chat on button click
        this.chatButton.on('click', () => {
            console.log('🖱️ AI button clicked');
            this.toggleChat();
        });

        // Close chat
        this.chatWindow.find('.ai-close').on('click', () => {
            console.log('❌ Close button clicked');
            this.closeChat();
        });

        // New chat button
        this.chatWindow.find('.ai-new-chat').on('click', () => {
            console.log('🆕 New chat button clicked');
            this.startNewChat();
        });

        // Load more messages button
        this.chatWindow.find('.load-more-btn').on('click', () => {
            console.log('📄 Load more messages clicked');
            this.loadMoreMessages();
        });

        // Send message on Enter key
        this.chatWindow.find('.ai-input').on('keypress', (e) => {
            if (e.which === 13) {
                console.log('⌨️ Enter key pressed');
                this.sendMessage();
            }
        });

        // Send message on button click
        this.chatWindow.find('.ai-send').on('click', () => {
            console.log('📤 Send button clicked');
            this.sendMessage();
        });

        // Prevent chat window from closing when clicking inside
        this.chatWindow.on('click', (e) => {
            e.stopPropagation();
        });

        // Close chat when clicking outside
        $(document).on('click', (e) => {
            if (this.isOpen && !$(e.target).closest('.ai-button, .ai-pane').length) {
                this.closeChat();
            }
        });

        // Handle window resize
        $(window).on('resize', () => {
            if (this.isOpen) {
                this.adjustChatPosition();
            }
        });

        console.log('✅ Events bound successfully');
    }

    toggleChat() {
        console.log('🔄 Toggling chat, current state:', this.isOpen);
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }

    openChat() {
        console.log('📖 Opening chat...');
        this.isOpen = true;
        this.chatButton.hide();
        this.chatWindow.addClass('ai-open').removeClass('ai-closed');
        
        // Auto-scroll to bottom when opening
        setTimeout(() => {
            this.scrollToBottom();
        }, 100);
        
        // Load recent chat session if no current chat
        if (!this.currentChatId) {
            this.loadRecentChatSession();
        }
        
        // Focus on input
        this.chatWindow.find('.ai-input').focus();
        
        console.log('✅ Chat opened successfully');
    }

    closeChat() {
        console.log('🔒 Closing AI chat...');
        
        // Use CSS classes for more reliable control
        $('.ai-pane').removeClass('ai-open').addClass('ai-closed');
        $('.ai-button').show();
        
        this.isOpen = false;
        console.log('✅ Chat closed successfully');
    }

    async sendMessage() {
        const input = this.chatWindow.find('.ai-input');
        const message = input.val().trim();
        
        if (!message) return;

        // Clear input and disable send button
        input.val('');
        this.chatWindow.find('.ai-send').prop('disabled', true);

        // Add user message to chat
        this.addMessage(message, 'user');

        // Show typing indicator
        this.showTyping();

        try {
            // Send to backend with current chat_id
            const response = await frappe.call({
                method: 'erpnext.ai_assistant.ai_chat.chat_with_ai',
                args: { 
                    message: message,
                    chat_id: this.currentChatId
                }
            });

            this.hideTyping();

            if (response.message.success) {
                // Update current chat ID from response
                if (response.message.chat_id) {
                    this.currentChatId = response.message.chat_id;
                }
                
                // Add AI response
                this.addMessage(response.message.response, 'ai');

                // Add action buttons if any
                if (response.message.actions && response.message.actions.length > 0) {
                    this.addActionButtons(response.message.actions);
                }
            } else {
                this.addMessage('Sorry, I encountered an error. Please try again.', 'ai');
            }
        } catch (error) {
            this.hideTyping();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'ai');
            console.error('AI Chat Error:', error);
        }

        // Re-enable send button
        this.chatWindow.find('.ai-send').prop('disabled', false);
    }

    addMessage(text, sender, prepend = false) {
        const messageClass = sender === 'user' ? 'user-message' : 'ai-message';
        const messageElement = $(`<div class="${messageClass}">${text}</div>`);
        
        const messagesContainer = this.chatWindow.find('.ai-messages-content');
        
        if (prepend) {
            messagesContainer.prepend(messageElement);
        } else {
            messagesContainer.append(messageElement);
            this.scrollToBottom();
        }
        
        // Check if we need to limit messages (keep only latest 25 in view)
        const messages = messagesContainer.children('.ai-message, .user-message');
        if (messages.length > this.messagesPerPage && !prepend) {
            // Remove oldest messages but keep them in history
            messages.slice(0, messages.length - this.messagesPerPage).remove();
            this.hasMoreMessages = true;
            this.chatWindow.find('.ai-load-more').show();
        }
    }

    addActionButtons(actions) {
        const actionsContainer = $('<div class="ai-actions"></div>');
        
        actions.forEach(action => {
            const button = $(`<button class="action-button" data-action="${action.type}">${action.description}</button>`);
            button.on('click', () => this.executeAction(action));
            actionsContainer.append(button);
        });

        this.chatWindow.find('.ai-messages-content').append(actionsContainer);
        this.scrollToBottom();
    }

    async executeAction(action) {
        try {
            // For now, we'll implement basic actions
            // You can extend this based on your needs
            const parameters = this.getActionParameters(action.type);
            
            const response = await frappe.call({
                method: 'erpnext.ai_assistant.ai_chat.execute_ai_action',
                args: {
                    action_type: action.type,
                    parameters: JSON.stringify(parameters)
                }
            });

            if (response.message.success) {
                this.addMessage(response.message.message, 'ai');
            } else {
                this.addMessage('Failed to execute action: ' + response.message.message, 'ai');
            }
        } catch (error) {
            this.addMessage('Error executing action. Please try again.', 'ai');
            console.error('Action execution error:', error);
        }
    }

    getActionParameters(actionType) {
        // Basic parameter extraction - can be enhanced
        switch (actionType) {
            case 'create_task':
                return {
                    subject: 'AI Generated Task',
                    description: 'Task created by AI Assistant'
                };
            case 'create_event':
                return {
                    subject: 'AI Generated Event',
                    description: 'Event created by AI Assistant'
                };
            case 'create_todo':
                return {
                    description: 'Todo created by AI Assistant'
                };
            default:
                return {};
        }
    }

    showTyping() {
        this.chatWindow.find('.ai-typing').show();
        this.scrollToBottom();
    }

    hideTyping() {
        this.chatWindow.find('.ai-typing').hide();
    }

    scrollToBottom() {
        const messagesContainer = this.chatWindow.find('.ai-messages-content');
        messagesContainer.scrollTop(messagesContainer[0].scrollHeight);
    }

    async startNewChat() {
        console.log('🆕 Starting new chat...');
        
        // Clear current messages
        this.chatWindow.find('.ai-messages-content').empty();
        this.chatWindow.find('.ai-load-more').hide();
        
        // Reset pagination and chat session
        this.messageOffset = 0;
        this.hasMoreMessages = false;
        this.currentChatId = null; // This will create a new session on next message
        
        // Show welcome message
        this.addMessage('Hello! I\'m your OMEX ERP AI Assistant. I can help you with:\n\n• Querying data (sales, inventory, etc.)\n• Creating tasks and events\n• Generating reports\n• Workflow automation\n\nWhat would you like to know?', 'ai');
        
        console.log('✅ New chat started');
    }

    async loadMoreMessages() {
        if (this.isLoadingMessages || !this.hasMoreMessages) {
            return;
        }

        console.log('📄 Loading more messages...');
        this.isLoadingMessages = true;
        
        const loadMoreBtn = this.chatWindow.find('.load-more-btn');
        loadMoreBtn.prop('disabled', true).text('Loading...');

        try {
            const response = await frappe.call({
                method: 'erpnext.ai_assistant.ai_chat.get_chat_history',
                args: { 
                    limit: this.messagesPerPage,
                    offset: this.messageOffset,
                    chat_id: this.currentChatId
                }
            });

            if (response.message && response.message.length > 0) {
                // Store current scroll position
                const messagesContainer = this.chatWindow.find('.ai-messages-content');
                const scrollHeight = messagesContainer[0].scrollHeight;
                
                // Add messages at the top (in reverse order)
                response.message.reverse().forEach(chat => {
                    this.addMessage(chat.response, 'ai', true);
                    this.addMessage(chat.message, 'user', true);
                });

                // Update pagination
                this.messageOffset += response.message.length;
                
                // Check if there are more messages
                if (response.message.length < this.messagesPerPage) {
                    this.hasMoreMessages = false;
                    this.chatWindow.find('.ai-load-more').hide();
                }

                // Maintain scroll position
                const newScrollHeight = messagesContainer[0].scrollHeight;
                messagesContainer.scrollTop(newScrollHeight - scrollHeight);
                
            } else {
                this.hasMoreMessages = false;
                this.chatWindow.find('.ai-load-more').hide();
            }
        } catch (error) {
            console.error('Error loading more messages:', error);
            frappe.msgprint('Failed to load more messages. Please try again.');
        } finally {
            this.isLoadingMessages = false;
            loadMoreBtn.prop('disabled', false).text('Load More Messages');
        }
    }

    adjustChatPosition() {
        // Adjust chat position if needed for responsive design
        const windowWidth = $(window).width();
        if (windowWidth < 768) {
            this.chatWindow.css('width', '100%');
        } else {
            this.chatWindow.css('width', '400px');
        }
    }

    async loadChatHistory() {
        try {
            const response = await frappe.call({
                method: 'erpnext.ai_assistant.ai_chat.get_chat_history',
                args: { 
                    limit: this.messagesPerPage,
                    offset: this.messageOffset,
                    chat_id: this.currentChatId
                }
            });

            if (response.message && response.message.length > 0) {
                // Set current chat ID from the latest message if not already set
                if (!this.currentChatId && response.message[0].chat_id) {
                    this.currentChatId = response.message[0].chat_id;
                }
                
                // Add recent messages (in reverse order to show oldest first)
                response.message.reverse().forEach(chat => {
                    this.addMessage(chat.message, 'user');
                    this.addMessage(chat.response, 'ai');
                });

                // Update pagination state
                this.messageOffset = response.message.length;
                
                // Check if there are more messages to load
                if (response.message.length === this.messagesPerPage) {
                    this.hasMoreMessages = true;
                    this.chatWindow.find('.ai-load-more').show();
                }
                
                // Auto-scroll to bottom to show latest messages
                setTimeout(() => {
                    this.scrollToBottom();
                }, 100);
                
            } else if (!this.currentChatId) {
                // Welcome message for new users only if no current session
                this.addMessage('Hello! I\'m your OMEX ERP AI Assistant. I can help you with:\n\n• Querying data (sales, inventory, etc.)\n• Creating tasks and events\n• Generating reports\n• Workflow automation\n\nWhat would you like to know?', 'ai');
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
            if (!this.currentChatId) {
                this.addMessage('Hello! I\'m your OMEX ERP AI Assistant. How can I help you today?', 'ai');
            }
        }
    }

    async loadRecentChatSession() {
        try {
            console.log('🔍 Loading recent chat session...');
            
            // Get the most recent chat session ID
            const sessionResponse = await frappe.call({
                method: 'erpnext.ai_assistant.ai_chat.get_recent_chat_session'
            });
            
            if (sessionResponse.message && sessionResponse.message.chat_id) {
                this.currentChatId = sessionResponse.message.chat_id;
                console.log('📝 Found recent chat session:', this.currentChatId);
                
                // Load messages for this specific session
                await this.loadChatHistory();
            } else {
                console.log('🆕 No previous chat session found, starting fresh');
                // Show welcome message for new users
                this.addMessage('Hello! I\'m your OMEX ERP AI Assistant. I can help you with:\n\n• Querying data (sales, inventory, etc.)\n• Creating tasks and events\n• Generating reports\n• Workflow automation\n\nWhat would you like to know?', 'ai');
            }
        } catch (error) {
            console.error('Error loading recent chat session:', error);
            this.addMessage('Hello! I\'m your OMEX ERP AI Assistant. How can I help you today?', 'ai');
        }
    }
}

// Initialize AI Assistant when page loads
$(document).ready(function() {
    console.log('AI Assistant script loaded, checking conditions...');
    console.log('Current path:', window.location.pathname);
    console.log('Frappe available:', !!window.frappe);
    console.log('User:', window.frappe?.session?.user);
    
    // Initialize on all pages except login and setup
    if (!window.location.pathname.includes('/login') && 
        !window.location.pathname.includes('/setup') &&
        !window.location.pathname.includes('/update') &&
        window.frappe && frappe.session.user !== 'Guest') {
        try {
            console.log('Initializing AI Assistant...');
            window.aiAssistant = new AIAssistant();
        } catch (error) {
            console.error('Error initializing AI Assistant:', error);
        }
    } else {
        console.log('AI Assistant not initialized due to conditions not met');
    }

    // Check if there are any existing elements trying to load chatbot-icon.svg
    setTimeout(() => {
        $('img[src*="chatbot-icon"]').each(function() {
            console.log('🚨 Found old chatbot icon reference:', $(this).attr('src'));
            console.log('🚨 Element:', this);
        });
    }, 2000);
});

// Also try to initialize after frappe is ready
if (typeof frappe !== 'undefined' && frappe.ready) {
    frappe.ready(function() {
        if (!window.aiAssistant && frappe.session.user !== 'Guest') {
            console.log('Initializing AI Assistant via frappe.ready...');
            try {
                window.aiAssistant = new AIAssistant();
            } catch (error) {
                console.error('Error initializing AI Assistant via frappe.ready:', error);
            }
        }
    });
} else if (typeof frappe !== 'undefined' && !window.aiAssistant && frappe.session.user !== 'Guest') {
    // Alternative initialization if frappe.ready is not available
    setTimeout(function() {
        if (!window.aiAssistant) {
            console.log('Initializing AI Assistant via timeout fallback...');
            try {
                window.aiAssistant = new AIAssistant();
            } catch (error) {
                console.error('Error initializing AI Assistant via timeout:', error);
            }
        }
    }, 1000);
}

// Manual trigger function for testing
window.createAIAssistant = function() {
    console.log(' Manual AI Assistant creation triggered');
    try {
        if (window.aiAssistant) {
            console.log('Removing existing AI Assistant');
            $('.ai-button').remove();
            $('.ai-pane').remove();
        }
        window.aiAssistant = new AIAssistant();
        console.log(' Manual AI Assistant created successfully');
    } catch (error) {
        console.error(' Error in manual AI Assistant creation:', error);
    }
};

// Manual reset function
window.resetAIChat = function() {
    console.log('🔄 Manual AI Chat reset triggered');
    try {
        // Force hide all AI elements
        $('.ai-pane').hide();
        $('.ai-button').show();
        
        if (window.aiAssistant) {
            window.aiAssistant.isOpen = false;
        }
        
        console.log(' AI Chat reset successfully');
    } catch (error) {
        console.error(' Error in AI Chat reset:', error);
    }
};

// Force close function
window.forceCloseAIChat = function() {
    console.log('🚫 Force closing AI Chat');
    $('.ai-pane').hide();
    $('.ai-button').show();
    if (window.aiAssistant) {
        window.aiAssistant.isOpen = false;
    }
    console.log(' AI Chat force closed');
};

// Manual testing functions
window.testOpenChat = function() {
    console.log('🧪 Manual test: Opening chat');
    $('.ai-pane').removeClass('ai-closed').addClass('ai-open');
    $('.ai-button').hide();
    if (window.aiAssistant) {
        window.aiAssistant.isOpen = true;
    }
    console.log('✅ Manual chat open test completed');
    console.log('Chat pane display:', $('.ai-pane').css('display'));
    console.log('Chat pane classes:', $('.ai-pane').attr('class'));
};

window.testCloseChat = function() {
    console.log('🧪 Manual test: Closing chat');
    $('.ai-pane').removeClass('ai-open').addClass('ai-closed');
    $('.ai-button').show();
    if (window.aiAssistant) {
        window.aiAssistant.isOpen = false;
    }
    console.log('✅ Manual chat close test completed');
};

window.testToggleChat = function() {
    console.log('🧪 Manual test: Toggling chat');
    if (window.aiAssistant) {
        window.aiAssistant.toggleChat();
    } else {
        console.log('❌ AI Assistant not found');
    }
}; 