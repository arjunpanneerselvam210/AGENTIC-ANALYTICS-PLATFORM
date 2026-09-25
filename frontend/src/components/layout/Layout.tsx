import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { AddDataSourceModal } from './AddDataSourceModal';

export const Layout: React.FC = () => {
  const [isAddDataSourceOpen, setIsAddDataSourceOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#070B12] text-slate-100 flex">
      {/* Fixed Left Sidebar */}
      <Sidebar onAddDataSource={() => setIsAddDataSourceOpen(true)} />

      {/* Main Content Area */}
      <div className="flex-1 pl-64 flex flex-col min-w-0">
        <Header />

        {/* Dynamic Page Outlet */}
        <main className="flex-1 mt-16 p-6 sm:p-8 max-w-7xl w-full mx-auto animate-fadeIn">
          <Outlet />
        </main>
      </div>

      {/* Add Data Source Modal */}
      <AddDataSourceModal
        isOpen={isAddDataSourceOpen}
        onClose={() => setIsAddDataSourceOpen(false)}
      />
    </div>
  );
};
