
import { useState, useRef, useEffect } from "react";
import { ChevronDown, MessageCircle, X, Send, Bot, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
}

const FAQ: Record<string, string> = {
  'diseases': "Our AI can help detect several eye diseases, including diabetic retinopathy, glaucoma, and cataracts. Upload a clear retinal image to get started.",
  'what diseases': "The main diseases detected by our AI are diabetic retinopathy, glaucoma, and cataracts. We are working to expand this list in the future!",
  'can be detected': "Currently, our AI detects diabetic retinopathy, glaucoma, and cataracts from retinal images.",
  'detect': "Our AI is designed to detect diabetic retinopathy, glaucoma, and cataracts. Please upload a retinal image for analysis.",
  'diabetic retinopathy': "Diabetic retinopathy is a diabetes complication that affects eyes. It's caused by damage to blood vessels in the retina. Our AI can detect signs of this condition, but professional diagnosis is essential.",
  'glaucoma': "Glaucoma is a group of eye conditions that damage the optic nerve, often due to high eye pressure. Early detection is crucial as it can cause gradual vision loss without symptoms.",
  'cataract': "Cataracts cause clouding of the eye's natural lens, leading to blurry vision. They're common with aging and can be treated with surgery. Our AI can identify cataract formations in retinal images.",
  'how does ai work': "Our AI uses a deep learning model (EfficientNetB0) trained on thousands of retinal images. It analyzes patterns in your uploaded image to detect signs of various eye diseases with 89% accuracy.",
  'how ai works': "Our AI uses advanced deep learning to analyze retinal images and detect diseases with high accuracy.",
  'accuracy': "Our AI model achieves 89% accuracy on validation datasets. However, results should always be confirmed by a qualified eye care professional.",
  'ai accuracy': "The AI is about 89% accurate on test data, but always consult a doctor for a final diagnosis.",
  'upload image': "To upload an image: 1) Click the upload area or drag & drop your retinal image 2) Ensure it's a clear fundus photograph 3) Wait for AI analysis 4) Review results and download report if needed.",
  'how to upload': "Click the upload area or drag and drop your retinal image. Make sure the image is clear for best results.",
  'how to use': "Upload a clear retinal image, wait for the AI to analyze it, and review the results. You can also ask me about eye diseases or the AI itself!",
  'hello': "Hello! How can I assist you with eye disease detection or using our AI tool today?",
  'hi': "Hi there! Ask me anything about eye diseases, our AI, or how to use this tool.",
  'help': "I'm here to help! You can ask about diseases, how the AI works, or how to use the tool."
};

export const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([{
    id: '1',
    type: 'bot',
    content: "Hi! I'm your AI assistant. I can help answer questions about eye diseases, how our AI works, or guide you through using this tool. What would you like to know?",
    timestamp: new Date()
  }]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [showScrollBtn, setShowScrollBtn] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom on new message
  useEffect(() => {
    if (isOpen && scrollRef.current) {
      setTimeout(() => {
        if (scrollRef.current) {
          scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
      }, 0);
    }
  }, [messages, isOpen]);

  // Show scroll button if not at bottom
  useEffect(() => {
    const handleScroll = () => {
      if (!scrollRef.current) return;
      const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
      setShowScrollBtn(scrollTop + clientHeight < scrollHeight - 20);
    };
    const ref = scrollRef.current;
    if (ref) ref.addEventListener('scroll', handleScroll);
    return () => {
      if (ref) ref.removeEventListener('scroll', handleScroll);
    };
  }, [isOpen]);

  const scrollToBottom = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || loading) return;
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    // Flexible matching: match any FAQ key as substring or token
    const lowerInput = inputValue.toLowerCase();
    const tokens = lowerInput.split(/\W+/).filter(Boolean);
    let botResponse = null;
    for (const [keyword, response] of Object.entries(FAQ)) {
      const keywordTokens = keyword.split(/\W+/).filter(Boolean);
      if (
        tokens.some(token => keywordTokens.includes(token)) ||
        lowerInput.includes(keyword) ||
        keywordTokens.some(kt => lowerInput.includes(kt))
      ) {
        botResponse = response;
        break;
      }
    }
    await new Promise((res) => setTimeout(res, 1200));
    const fallback = "Sorry, I couldn't find an answer to that. Please try rephrasing your question or ask about eye diseases, AI, or how to use this tool.";
    const lastBotMsg = messages.filter(m => m.type === 'bot').slice(-1)[0]?.content;
    const nextBotMsg = botResponse || (lastBotMsg === fallback ? "I'm still learning! Please ask about eye diseases, our AI, or how to use this tool." : fallback);
    setMessages(prev => [
      ...prev,
      {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: nextBotMsg,
        timestamp: new Date()
      }
    ]);
    setLoading(false);
    setInputValue('');
  };

  const quickQuestions = [
    "How accurate is the AI?",
    "What is diabetic retinopathy?",
    "How do I upload an image?",
    "What diseases can be detected?"
  ];

  return (
    <>
      {/* Chat Toggle Button */}
      <Button
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-4 right-4 w-14 h-14 rounded-full shadow-neon bg-gradient-to-r from-neon-cyan to-neon-purple hover:shadow-neon-lg transition-all duration-300 z-50 ${isOpen ? 'hidden' : 'flex'} sm:bottom-6 sm:right-6`}
        aria-label="Open chat"
      >
        <MessageCircle className="w-6 h-6" />
      </Button>

      {/* Chat Window */}
      {isOpen && (
        <Card
          className="fixed bottom-0 left-0 right-0 mx-auto w-full max-w-[95vw] sm:max-w-md h-[70vh] sm:bottom-6 sm:right-6 sm:left-auto sm:w-96 sm:h-[32rem] flex flex-col shadow-2xl border-neon-cyan/30 bg-card/95 backdrop-blur-sm z-50 rounded-t-xl sm:rounded-xl overflow-hidden"
        >
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bot className="w-5 h-5 text-neon-cyan" />
                <span className="text-lg">AI Assistant</span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsOpen(false)}
                className="h-8 w-8 p-0"
                aria-label="Close chat"
              >
                <X className="w-4 h-4" />
              </Button>
            </CardTitle>
          </CardHeader>

          <CardContent className="flex-1 flex flex-col p-2 pt-0 sm:p-4 sm:pt-0 overflow-hidden">
            {/* Messages */}
            <div className="flex-1 relative overflow-hidden">
              <div
                ref={scrollRef}
                className="h-full w-full overflow-y-auto overflow-x-hidden space-y-3 pr-2"
                style={{ maxHeight: '100%', minHeight: 0 }}
              >
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-2 w-full ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    {message.type === 'bot' && (
                      <Bot className="w-6 h-6 text-neon-cyan mt-1 flex-shrink-0" />
                    )}
                    <div
                      className={`w-full max-w-[80vw] sm:max-w-[80%] p-2 sm:p-3 rounded-lg text-sm break-words break-all whitespace-pre-line overflow-hidden ${
                        message.type === 'user'
                          ? 'bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30'
                          : 'bg-muted text-foreground'
                      }`}
                      style={{ wordBreak: 'break-all' }}
                    >
                      {message.content}
                    </div>
                    {message.type === 'user' && (
                      <User className="w-6 h-6 text-neon-purple mt-1 flex-shrink-0" />
                    )}
                  </div>
                ))}
                {loading && (
                  <div className="flex gap-2 items-center w-full">
                    <Bot className="w-6 h-6 text-neon-cyan mt-1 flex-shrink-0 animate-pulse" />
                    <div className="w-full max-w-[80vw] sm:max-w-[80%] p-2 sm:p-3 rounded-lg text-sm bg-muted text-foreground opacity-80 animate-pulse break-all overflow-hidden">
                      AI is typing...
                    </div>
                  </div>
                )}
              </div>
              {showScrollBtn && (
                <button
                  onClick={scrollToBottom}
                  className="absolute right-2 bottom-4 z-10 bg-background/80 hover:bg-background border border-neon-cyan/40 rounded-full p-2 shadow-lg transition-all"
                  aria-label="Scroll to bottom"
                >
                  <ChevronDown className="w-5 h-5 text-neon-cyan" />
                </button>
              )}
            </div>

            {/* Quick Questions */}
            {messages.length === 1 && !loading && (
              <div className="mb-2 sm:mb-4">
                <p className="text-sm text-muted-foreground mb-2">Quick questions:</p>
                <div className="flex flex-wrap gap-2">
                  {quickQuestions.map((question) => (
                    <Button
                      key={question}
                      variant="outline"
                      size="sm"
                      onClick={() => setInputValue(question)}
                      className="text-xs border-neon-cyan/30 hover:border-neon-cyan/50 hover:bg-neon-cyan/10"
                    >
                      {question}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {/* Input Area */}
            <div className="flex gap-2 mt-2">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Ask me anything..."
                className="flex-1 border-neon-cyan/30 focus:border-neon-cyan text-xs sm:text-base"
                disabled={loading}
                autoFocus
              />
              <Button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || loading}
                className="bg-gradient-to-r from-neon-cyan to-neon-purple hover:shadow-neon"
                aria-label="Send message"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </>
  );
};