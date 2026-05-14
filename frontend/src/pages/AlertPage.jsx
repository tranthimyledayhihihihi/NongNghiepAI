import { useState } from 'react';
import AlertHistory from '../components/Alert/AlertHistory';
import AlertSubscribe from '../components/Alert/AlertSubscribe';

const AlertPage = () => {
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <div className="px-4 py-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Canh bao bien dong gia
        </h1>
        <p className="mt-2 text-gray-600">
          Tao, xem va tat canh bao gia qua API backend.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AlertSubscribe onCreated={() => setRefreshKey((value) => value + 1)} />
        <AlertHistory refreshKey={refreshKey} />
      </div>
    </div>
  );
};

export default AlertPage;
