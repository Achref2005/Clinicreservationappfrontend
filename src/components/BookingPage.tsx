import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Send, Mic, MicOff, Bot } from 'lucide-react';
import { toast } from 'sonner@2.0.3';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

export function BookingPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! I\'m here to help you book an appointment at MediCare Clinic. Could you please provide your full name?',
      sender: 'assistant',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Mock AI response logic
  const getAIResponse = (userMessage: string): string => {
    const lowerMessage = userMessage.toLowerCase();
    
    // Check for name patterns
    if (messages.length === 1) {
      return `Thank you! Now, could you please provide your phone number?`;
    }
    
    // Check for phone number
    if (messages.length === 3) {
      return `Great! What date and time would you prefer for your appointment? For example, you can say "Tomorrow at 2 PM" or "Next Monday at 10 AM".`;
    }
    
    // Check for date/time
    if (messages.length === 5) {
      return `Let me check the availability... Good news! That time slot is available. Would you like to confirm your appointment?`;
    }
    
    // Confirmation
    if (lowerMessage.includes('yes') || lowerMessage.includes('confirm')) {
      return `Perfect! Your appointment has been booked. You'll receive a reminder before your appointment. Is there anything else I can help you with?`;
    }
    
    if (lowerMessage.includes('no')) {
      return `No problem! What other time would work better for you?`;
    }
    
    // Default response
    return `I understand. Could you please provide more details so I can assist you better?`;
  };

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: getAIResponse(inputValue),
        sender: 'assistant',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiResponse]);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const toggleRecording = () => {
    if (!isRecording) {
      toast.info('Voice recording started. Speak now...');
      setIsRecording(true);
      
      // Simulate recording stop after 3 seconds
      setTimeout(() => {
        setIsRecording(false);
        toast.success('Voice message recorded');
        setInputValue('I would like to book an appointment for tomorrow at 2 PM');
      }, 3000);
    } else {
      setIsRecording(false);
      toast.info('Recording stopped');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-6">
          <h1 className="text-slate-900 mb-2">Book an Appointment</h1>
          <p className="text-slate-600">
            Chat with our booking assistant to schedule your appointment
          </p>
        </div>

        {/* Chat Interface */}
        <Card className="shadow-lg">
          <CardHeader className="bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-t-lg">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                <Bot className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-white">Booking Assistant</h2>
                <p className="text-blue-100">Online</p>
              </div>
            </div>
          </CardHeader>
          
          <CardContent className="p-0">
            {/* Messages Area */}
            <div className="h-[500px] overflow-y-auto p-6 space-y-4 bg-slate-50">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[75%] rounded-lg px-4 py-3 ${
                      message.sender === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-slate-900 shadow-sm border border-slate-200'
                    }`}
                  >
                    <p className={message.sender === 'user' ? 'text-white' : 'text-slate-900'}>
                      {message.text}
                    </p>
                    <span
                      className={`text-xs mt-1 block ${
                        message.sender === 'user' ? 'text-blue-200' : 'text-slate-500'
                      }`}
                    >
                      {message.timestamp.toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-slate-200 p-4 bg-white rounded-b-lg">
              <div className="flex items-end gap-2">
                <Button
                  type="button"
                  variant={isRecording ? 'default' : 'outline'}
                  size="icon"
                  onClick={toggleRecording}
                  className={isRecording ? 'bg-red-600 hover:bg-red-700' : ''}
                >
                  {isRecording ? (
                    <MicOff className="w-5 h-5" />
                  ) : (
                    <Mic className="w-5 h-5" />
                  )}
                </Button>
                
                <Input
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message..."
                  className="flex-1"
                  disabled={isRecording}
                />
                
                <Button
                  type="button"
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isRecording}
                  size="icon"
                >
                  <Send className="w-5 h-5" />
                </Button>
              </div>
              <p className="text-slate-500 mt-2 text-center">
                Press the microphone button to use voice input, or type your message
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Info Card */}
        <Card className="mt-6 bg-blue-50 border-blue-200">
          <CardContent className="pt-6">
            <p className="text-slate-700">
              <strong>How it works:</strong> Our booking assistant will ask for your name, phone number, 
              and preferred appointment time. The system will check availability and confirm your booking. 
              You'll receive a reminder before your appointment.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
