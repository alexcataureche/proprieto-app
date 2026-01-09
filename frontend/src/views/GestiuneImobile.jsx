import React, { useState } from 'react';
import { Plus, Edit2, Trash2, Info } from 'lucide-react';

const GestiuneImobile = () => {
  const [imobile, setImobile] = useState([
    {
      id: 1,
      numeIdentificare: 'Apartament Centru Cluj',
      procentProprietate: 100,
      coproprietari: [],
    },
    {
      id: 2,
      numeIdentificare: 'Casa Ploiești',
      procentProprietate: 50,
      coproprietari: ['Ionescu Maria'],
    },
    {
      id: 3,
      numeIdentificare: 'Studio București',
      procentProprietate: 75,
      coproprietari: ['Popescu Ion'],
    },
  ]);

  const [showAddForm, setShowAddForm] = useState(false);
  const [isAdmin, setIsAdmin] = useState(true); // Simulate admin mode

  return (
    <div className="min-h-screen bg-app-bg pt-20 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Admin Banner */}
        {isAdmin && (
          <div className="admin-banner mb-6">
            <div className="flex items-center">
              <Info className="w-5 h-5 mr-2" />
              <span className="font-medium">
                Mod Administrator: Vezi toate imobilele sau filtrează după utilizator
              </span>
            </div>
          </div>
        )}

        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-navy">
            Gestiune Portofoliu Imobiliar
          </h1>
          <button
            onClick={() => setShowAddForm(true)}
            className="btn-primary flex items-center space-x-2"
          >
            <Plus className="w-5 h-5" />
            <span>Adaugă Imobil Nou</span>
          </button>
        </div>

        {/* Properties Table */}
        <div className="card">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-navy-200">
              <thead>
                <tr className="bg-navy-50">
                  <th className="px-6 py-3 text-left text-xs font-semibold text-navy uppercase tracking-wider">
                    Nume Identificare
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-navy uppercase tracking-wider">
                    Procent Proprietate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-navy uppercase tracking-wider">
                    Nume Co-Proprietar
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-semibold text-navy uppercase tracking-wider">
                    Acțiuni
                  </th>
                </tr>
              </thead>
              <tbody className="bg-surface divide-y divide-navy-200">
                {imobile.map((imobil) => (
                  <tr key={imobil.id} className="table-row-hover">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-bold text-navy">
                        {imobil.numeIdentificare}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {imobil.procentProprietate === 100 ? (
                        <span className="badge-success">
                          {imobil.procentProprietate}%
                        </span>
                      ) : (
                        <span className="badge-warning">
                          {imobil.procentProprietate}%
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-navy-500">
                        {imobil.coproprietari.length > 0
                          ? imobil.coproprietari.join(', ')
                          : '-'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-3">
                        <button
                          onClick={() => console.log('Edit', imobil.id)}
                          className="text-primary hover:text-primary-700 transition-colors"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => console.log('Delete', imobil.id)}
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

        {/* Empty State */}
        {imobile.length === 0 && (
          <div className="card text-center py-12">
            <div className="text-navy-400 mb-4">
              <Building2 className="w-16 h-16 mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-navy mb-2">
              Niciun imobil înregistrat
            </h3>
            <p className="text-navy-500 mb-6">
              Începe prin a adăuga primul tău imobil
            </p>
            <button
              onClick={() => setShowAddForm(true)}
              className="btn-primary inline-flex items-center space-x-2"
            >
              <Plus className="w-5 h-5" />
              <span>Adaugă Imobil Nou</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default GestiuneImobile;
