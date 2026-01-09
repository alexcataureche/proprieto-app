import React from 'react';
import { BarChart3, TrendingUp, DollarSign, FileText } from 'lucide-react';

const DashboardFiscal = () => {
  const stats = [
    {
      id: 1,
      name: 'Venit Total Anual',
      value: '48,000 RON',
      icon: DollarSign,
      change: '+12%',
      changeType: 'increase',
    },
    {
      id: 2,
      name: 'Contracte Active',
      value: '12',
      icon: FileText,
      change: '+2',
      changeType: 'increase',
    },
    {
      id: 3,
      name: 'Imobile Închiriate',
      value: '8',
      icon: BarChart3,
      change: '0',
      changeType: 'neutral',
    },
    {
      id: 4,
      name: 'Rata de Ocupare',
      value: '92%',
      icon: TrendingUp,
      change: '+5%',
      changeType: 'increase',
    },
  ];

  return (
    <div className="min-h-screen bg-app-bg pt-20 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-navy mb-6">Dashboard Fiscal</h1>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <div key={stat.id} className="card">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-navy-500">
                      {stat.name}
                    </p>
                    <p className="text-2xl font-bold text-navy mt-2">
                      {stat.value}
                    </p>
                    {stat.changeType === 'increase' && (
                      <p className="text-sm text-success-text mt-1">
                        {stat.change} față de luna trecută
                      </p>
                    )}
                  </div>
                  <div className="flex-shrink-0">
                    <div className="p-3 bg-primary-50 rounded-lg">
                      <Icon className="w-6 h-6 text-primary" />
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Chart Placeholder */}
        <div className="card mb-6">
          <h2 className="text-xl font-bold text-navy mb-4">
            Venituri pe Luni - 2026
          </h2>
          <div className="h-64 flex items-center justify-center bg-navy-50 rounded-lg">
            <div className="text-center">
              <BarChart3 className="w-16 h-16 text-navy-300 mx-auto mb-2" />
              <p className="text-navy-500">Grafic în curând...</p>
            </div>
          </div>
        </div>

        {/* ANAF Report Section */}
        <div className="card">
          <h2 className="text-xl font-bold text-navy mb-4">Raport ANAF D212</h2>
          <p className="text-navy-600 mb-4">
            Generează raportul pentru declarația anuală ANAF D212.
          </p>
          <div className="flex space-x-4">
            <button className="btn-primary flex items-center space-x-2">
              <FileText className="w-4 h-4" />
              <span>Generează Raport 2026</span>
            </button>
            <button className="btn-secondary flex items-center space-x-2">
              <FileText className="w-4 h-4" />
              <span>Export Excel</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardFiscal;
