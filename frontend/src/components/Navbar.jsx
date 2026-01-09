import React from 'react';
import { Building2, FileText, BarChart3 } from 'lucide-react';

const Navbar = ({ activeView, onNavigate }) => {
  const menuItems = [
    { id: 'imobile', label: 'Gestiune Imobile', icon: Building2 },
    { id: 'contracte', label: 'Gestiune Contracte', icon: FileText },
    { id: 'dashboard', label: 'Dashboard Fiscal', icon: BarChart3 },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 bg-surface border-b border-navy-200 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-navy">PropManager</h1>
          </div>

          {/* Navigation Menu */}
          <div className="flex space-x-8">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeView === item.id;

              return (
                <button
                  key={item.id}
                  onClick={() => onNavigate(item.id)}
                  className={`
                    flex items-center space-x-2 px-1 py-2 text-sm font-medium
                    border-b-2 transition-colors
                    ${isActive
                      ? 'border-primary text-primary'
                      : 'border-transparent text-navy-600 hover:text-navy hover:border-navy-200'
                    }
                  `}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
