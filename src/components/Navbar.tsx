import { Link, useLocation } from 'react-router-dom';
import { Stethoscope, Calendar, Users, Phone, Home } from 'lucide-react';

export function Navbar() {
  const location = useLocation();
  
  const isActive = (path: string) => location.pathname === path;
  
  return (
    <nav className="bg-white shadow-sm border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Stethoscope className="w-6 h-6 text-white" />
            </div>
            <span className="text-slate-900">MediCare Clinic</span>
          </Link>
          
          <div className="flex items-center gap-1">
            <Link 
              to="/"
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                isActive('/') 
                  ? 'bg-blue-50 text-blue-600' 
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              <Home className="w-4 h-4" />
              <span>Home</span>
            </Link>
            
            <Link 
              to="/doctors"
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                isActive('/doctors') 
                  ? 'bg-blue-50 text-blue-600' 
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              <Users className="w-4 h-4" />
              <span>Doctors</span>
            </Link>
            
            <Link 
              to="/appointments"
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                isActive('/appointments') 
                  ? 'bg-blue-50 text-blue-600' 
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              <Calendar className="w-4 h-4" />
              <span>My Appointments</span>
            </Link>
            
            <Link 
              to="/contact"
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                isActive('/contact') 
                  ? 'bg-blue-50 text-blue-600' 
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              <Phone className="w-4 h-4" />
              <span>Contact</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
