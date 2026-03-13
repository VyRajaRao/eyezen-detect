import { Heart, Github, Linkedin, Mail, Eye } from "lucide-react";

export const Footer = () => {
  return (
    <footer className="bg-card/50 backdrop-blur-sm border-t border-border py-12">
      <div className="max-w-6xl mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <Eye className="w-8 h-8 text-neon-cyan" />
              <h3 className="text-2xl font-bold bg-gradient-to-r from-neon-cyan to-neon-purple bg-clip-text text-transparent">
                AI EyeScan
              </h3>
            </div>
            <p className="text-muted-foreground mb-4 max-w-md">
              Advanced AI-powered eye disease detection system for educational purposes. 
              Helping to democratize access to preliminary eye health screening through technology.
            </p>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span>Made with</span>
              <Heart className="w-4 h-4 text-neon-pink animate-pulse" />
              <span>for better eye health awareness</span>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-lg font-semibold mb-4 text-neon-purple">Quick Links</h4>
            <ul className="space-y-2 text-muted-foreground">
              <li><a href="#upload" className="hover:text-neon-cyan transition-colors">Upload Image</a></li>
              <li><a href="#about" className="hover:text-neon-cyan transition-colors">About AI</a></li>
              <li><a href="#disclaimer" className="hover:text-neon-cyan transition-colors">Disclaimer</a></li>
              <li><a href="#faq" className="hover:text-neon-cyan transition-colors">FAQ</a></li>
            </ul>
          </div>

          {/* Contact & Social */}
          <div>
            <h4 className="text-lg font-semibold mb-4 text-neon-pink">Connect</h4>
            <div className="space-y-3">
              <a 
                href="https://github.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-muted-foreground hover:text-neon-cyan transition-colors"
              >
                <Github className="w-4 h-4" />
                GitHub
              </a>
              <a 
                href="https://linkedin.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-muted-foreground hover:text-neon-cyan transition-colors"
              >
                <Linkedin className="w-4 h-4" />
                LinkedIn
              </a>
              <a 
                href="mailto:contact@eyescan.ai" 
                className="flex items-center gap-2 text-muted-foreground hover:text-neon-cyan transition-colors"
              >
                <Mail className="w-4 h-4" />
                Contact
              </a>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-border mt-8 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="text-sm text-muted-foreground">
            © 2024 AI EyeScan. Educational purposes only. Not for medical diagnosis.
          </div>
          <div className="flex gap-6 text-sm text-muted-foreground">
            <a href="#" className="hover:text-neon-cyan transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-neon-cyan transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-neon-cyan transition-colors">Medical Disclaimer</a>
          </div>
        </div>
      </div>
    </footer>
  );
};