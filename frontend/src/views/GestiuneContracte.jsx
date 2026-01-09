import React, { useState } from 'react';
import { Plus, Edit2, Trash2, FileText, Calendar, DollarSign } from 'lucide-react';
import { format } from 'date-fns';

const GestiuneContracte = () => {
  const [contracte, setContracte] = useState([
    {
      id: 1,
      chirias: {
        nume: 'Popescu Ion',
        telefon: '0722123456',
        email: 'popescu@email.com',
      },
      imobil: 'Apartament Centru Cluj',
      chirie: 2500,
      moneda: 'RON',
      dataInceput: '2024-01-01',
      dataSfarsit: '2024-12-31',
      status: 'activ',
    },
    {
      id: 2,
      chirias: {
        nume: 'Ionescu Maria',
        telefon: '0733987654',
        email: 'ionescu@email.com',
      },
      imobil: 'Casa Ploiești',
      chirie: 1500,
      moneda: 'RON',
      dataInceput: '2024-02-01',
      dataSfarsit: '2026-02-28',
      status: 'expiring',
    },
  ]);

  const [showAddForm, setShowAddForm] = useState(false);

  const getStatusBadge = (status) => {
    if (status === 'activ') {
      return <span className="badge-success">Activ</span>;
    } else if (status === 'expiring') {
      return <span className="badge-warning">Expiră în curând</span>;
    } else {
      return <span className="badge-danger">Expirat</span>;
    }
  };

  return (
    <div className="min-h-screen bg-app-bg pt-20 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-navy">
            Gestiune Contracte de Închiriere
          </h1>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="btn-primary flex items-center space-x-2"
          >
            <Plus className="w-5 h-5" />
            <span>Adaugă Contract Nou</span>
          </button>
        </div>

        {/* Add Contract Form */}
        {showAddForm && (
          <div className="card mb-6">
            <h2 className="text-xl font-bold text-navy mb-6">Contract Nou</h2>

            <form className="space-y-6">
              {/* Section: Date Contract */}
              <div>
                <h3 className="text-lg font-semibold text-navy mb-4 flex items-center">
                  <FileText className="w-5 h-5 mr-2" />
                  Date Contract
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">
                      Imobil *
                    </label>
                    <select className="select-field">
                      <option value="">Selectează imobil</option>
                      <option value="1">Apartament Centru Cluj</option>
                      <option value="2">Casa Ploiești</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">
                      Nr. Contract
                    </label>
                    <input
                      type="text"
                      placeholder="ex: C-2026-001"
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">
                      Link Document
                    </label>
                    <input
                      type="url"
                      placeholder="https://..."
                      className="input-field"
                    />
                  </div>
                </div>
              </div>

              {/* Section: Date Locatar */}
              <div>
                <h3 className="text-lg font-semibold text-navy mb-4 flex items-center">
                  <FileText className="w-5 h-5 mr-2" />
                  Date Locatar (Chiriaș)
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">
                      Tip Locatar *
                    </label>
                    <select className="select-field">
                      <option value="pf">Persoană Fizică</option>
                      <option value="pj">Persoană Juridică</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">
                      Nume Complet / Denumire *
                    </label>
                    <input
                      type="text"
                      placeholder="ex: Popescu Ion"
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">
                      CNP / CUI *
                    </label>
                    <input
                      type="text"
                      placeholder="13 cifre pentru PF, 2-10 pentru PJ"
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">
                      Telefon *
                    </label>
                    <input
                      type="tel"
                      placeholder="ex: 0722123456"
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">
                      Email
                    </label>
                    <input
                      type="email"
                      placeholder="email@example.com"
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">
                      Adresă *
                    </label>
                    <input
                      type="text"
                      placeholder="Adresa completă"
                      className="input-field"
                    />
                  </div>
                </div>
              </div>

              {/* Section: Date Financiare */}
              <div>
                <h3 className="text-lg font-semibold text-navy mb-4 flex items-center">
                  <DollarSign className="w-5 h-5 mr-2" />
                  Date Financiare și Perioada
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">
                      Chirie *
                    </label>
                    <input
                      type="number"
                      placeholder="0.00"
                      className="input-field"
                      step="0.01"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">
                      Monedă *
                    </label>
                    <select className="select-field">
                      <option value="RON">RON</option>
                      <option value="EUR">EUR</option>
                      <option value="USD">USD</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">
                      Frecvență *
                    </label>
                    <select className="select-field">
                      <option value="lunar">Lunar</option>
                      <option value="trimestrial">Trimestrial</option>
                      <option value="semestrial">Semestrial</option>
                      <option value="anual">Anual</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">
                      Data Început *
                    </label>
                    <input type="date" className="input-field" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">
                      Data Sfârșit
                    </label>
                    <input type="date" className="input-field" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-navy mb-2">
                      Nr. Camere
                    </label>
                    <input
                      type="number"
                      placeholder="0 = tot imobilul"
                      className="input-field"
                      min="0"
                    />
                  </div>
                </div>
              </div>

              {/* Form Actions */}
              <div className="flex items-center justify-end space-x-4 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="btn-secondary"
                >
                  Anulează
                </button>
                <button type="submit" className="btn-primary">
                  Salvează Contract
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Contracts Table */}
        <div className="card">
          <h2 className="text-xl font-bold text-navy mb-4">Contracte Active</h2>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-navy-200">
              <thead>
                <tr className="bg-navy-50">
                  <th className="px-6 py-3 text-left text-xs font-semibold text-navy uppercase tracking-wider">
                    Chiriaș
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-navy uppercase tracking-wider">
                    Imobil
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-navy uppercase tracking-wider">
                    Chirie
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-navy uppercase tracking-wider">
                    Valabilitate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-navy uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-semibold text-navy uppercase tracking-wider">
                    Acțiuni
                  </th>
                </tr>
              </thead>
              <tbody className="bg-surface divide-y divide-navy-200">
                {contracte.map((contract) => (
                  <tr key={contract.id} className="table-row-hover">
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm font-bold text-navy">
                          {contract.chirias.nume}
                        </div>
                        <div className="text-xs text-navy-500">
                          {contract.chirias.telefon}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-navy">
                        {contract.imobil}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-bold text-primary">
                        {contract.chirie} {contract.moneda}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-navy-500">
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-3 h-3" />
                          <span>
                            {contract.dataInceput} - {contract.dataSfarsit}
                          </span>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(contract.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-3">
                        <button
                          onClick={() => console.log('Edit', contract.id)}
                          className="text-primary hover:text-primary-700 transition-colors"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => console.log('Delete', contract.id)}
                          className="text-danger-text hover:text-red-700 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GestiuneContracte;
