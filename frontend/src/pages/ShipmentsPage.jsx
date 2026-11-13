import React, { useState, useEffect } from 'react';
import { Truck, Search, PlusCircle, CheckCircle2, Clock, AlertCircle, Eye, X } from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';
import { TrackingTimeline } from '../components/TrackingTimeline';
import { api } from '../services/api';

export function ShipmentsPage() {
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedShipment, setSelectedShipment] = useState(null);
  const [showEventModal, setShowEventModal] = useState(false);
  const [newEventStatus, setNewEventStatus] = useState('IN_TRANSIT');
  const [newEventLocation, setNewEventLocation] = useState('Chicago Hub Sorting Facility');
  const [newEventDesc, setNewEventDesc] = useState('Processed through distribution hub.');
  const [isSubmittingEvent, setIsSubmittingEvent] = useState(false);
  const [eventError, setEventError] = useState(null);

  const fetchShipments = async () => {
    setLoading(true);
    try {
      const data = await api.getShipments({ limit: 100 });
      setShipments(data);
    } catch (err) {
      console.error('Failed to fetch shipments:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchShipments();
  }, []);

  const openShipmentDetails = async (shp) => {
    try {
      const full = await api.getShipment(shp.shipment_id);
      setSelectedShipment(full);
    } catch (e) {
      setSelectedShipment(shp);
    }
  };

  const handleAddEvent = async (e) => {
    e.preventDefault();
    if (!selectedShipment) return;
    setIsSubmittingEvent(true);
    setEventError(null);

    try {
      await api.addTrackingEvent(selectedShipment.shipment_id, {
        event_status: newEventStatus,
        location: newEventLocation,
        description: newEventDesc,
      });
      // Refresh shipment
      const updated = await api.getShipment(selectedShipment.shipment_id);
      setSelectedShipment(updated);
      setShowEventModal(false);
      fetchShipments();
    } catch (err) {
      setEventError(err.message || 'Failed to record tracking event');
    } finally {
      setIsSubmittingEvent(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white">Carrier Shipments & Real-Time Tracking</h2>
        <p className="text-xs text-slate-400">
          Monitor dispatch schedules, carrier transit status, milestone events, and split package deliveries.
        </p>
      </div>

      {/* Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-950 text-slate-400 border-b border-slate-800">
                <th className="py-3 px-4 font-semibold">Shipment ID</th>
                <th className="py-3 px-4 font-semibold">Order ID</th>
                <th className="py-3 px-4 font-semibold">Origin Node</th>
                <th className="py-3 px-4 font-semibold">Carrier & Service</th>
                <th className="py-3 px-4 font-semibold">Tracking #</th>
                <th className="py-3 px-4 font-semibold">Status</th>
                <th className="py-3 px-4 font-semibold">Promised Delivery</th>
                <th className="py-3 px-4 font-semibold text-right">Cost</th>
                <th className="py-3 px-4 font-semibold text-center">Track</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {loading ? (
                <tr>
                  <td colSpan="9" className="py-12 text-center text-slate-500 font-sans">
                    Loading shipments...
                  </td>
                </tr>
              ) : shipments.length === 0 ? (
                <tr>
                  <td colSpan="9" className="py-12 text-center text-slate-500 font-sans">
                    No shipments found.
                  </td>
                </tr>
              ) : (
                shipments.map((s) => (
                  <tr key={s.shipment_id} className="hover:bg-slate-800/40">
                    <td className="py-3 px-4 font-bold text-sky-400">{s.shipment_id}</td>
                    <td className="py-3 px-4 text-slate-300">{s.order_id}</td>
                    <td className="py-3 px-4 font-sans text-slate-300">{s.node_name}</td>
                    <td className="py-3 px-4 font-sans text-slate-300">{s.carrier_name} ({s.service_name})</td>
                    <td className="py-3 px-4 text-slate-400">{s.tracking_number}</td>
                    <td className="py-3 px-4 font-sans"><StatusBadge status={s.shipment_status} /></td>
                    <td className="py-3 px-4 text-slate-300">
                      {s.promised_delivery_date ? s.promised_delivery_date.split('T')[0] : '-'}
                    </td>
                    <td className="py-3 px-4 text-right text-slate-200">${s.shipping_cost.toFixed(2)}</td>
                    <td className="py-3 px-4 text-center">
                      <button
                        onClick={() => openShipmentDetails(s)}
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-sky-400 text-[11px] font-sans font-medium transition"
                      >
                        Timeline
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Shipment Tracking Drawer */}
      {selectedShipment && (
        <div className="fixed inset-0 z-50 flex items-center justify-end bg-black/60 backdrop-blur-sm">
          <div className="w-full max-w-xl h-full bg-slate-900 border-l border-slate-800 p-6 overflow-y-auto shadow-2xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <div>
                  <h3 className="text-base font-bold text-white font-mono">{selectedShipment.shipment_id}</h3>
                  <p className="text-xs text-slate-400 mt-0.5">Tracking Number: {selectedShipment.tracking_number}</p>
                </div>
                <button
                  onClick={() => setSelectedShipment(null)}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-white"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Status Header */}
              <div className="py-4 border-b border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-xs text-slate-500 block mb-1">Current Lifecycle Status</span>
                  <StatusBadge status={selectedShipment.shipment_status} />
                </div>
                <button
                  onClick={() => setShowEventModal(true)}
                  className="px-3 py-1.5 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs font-semibold flex items-center gap-1.5"
                >
                  <PlusCircle className="w-3.5 h-3.5" />
                  <span>Log Milestone Event</span>
                </button>
              </div>

              {/* Timeline Container */}
              <div className="py-5">
                <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-4">Tracking Event Stream</h4>
                <TrackingTimeline events={selectedShipment.tracking_events} />
              </div>
            </div>

            <div className="pt-4 border-t border-slate-800 text-xs text-slate-500 text-center font-mono">
              Associated Order: {selectedShipment.order_id} • Origin: {selectedShipment.node_id}
            </div>
          </div>
        </div>
      )}

      {/* Add Tracking Event Modal */}
      {showEventModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-md w-full p-6 shadow-2xl relative">
            <button
              onClick={() => setShowEventModal(false)}
              className="absolute right-4 top-4 text-slate-400 hover:text-white p-1"
            >
              <X className="w-5 h-5" />
            </button>
            <h3 className="text-base font-bold text-white mb-1">Add Tracking Milestone</h3>
            <p className="text-xs text-slate-400 mb-4">
              State machine transition check will validate lifecycle rules.
            </p>

            {eventError && (
              <div className="mb-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
                {eventError}
              </div>
            )}

            <form onSubmit={handleAddEvent} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">Next Lifecycle Status</label>
                <select
                  value={newEventStatus}
                  onChange={(e) => setNewEventStatus(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-sky-500"
                >
                  <option value="IN_TRANSIT">IN_TRANSIT</option>
                  <option value="OUT_FOR_DELIVERY">OUT_FOR_DELIVERY</option>
                  <option value="DELIVERED">DELIVERED</option>
                  <option value="DELIVERY_DELAYED">DELIVERY_DELAYED</option>
                  <option value="DELIVERY_FAILED">DELIVERY_FAILED</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Event Location</label>
                <input
                  type="text"
                  required
                  value={newEventLocation}
                  onChange={(e) => setNewEventLocation(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-sky-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Description</label>
                <textarea
                  rows="2"
                  required
                  value={newEventDesc}
                  onChange={(e) => setNewEventDesc(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-sky-500"
                ></textarea>
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowEventModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingEvent}
                  className="px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold"
                >
                  {isSubmittingEvent ? 'Recording...' : 'Commit Event'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
