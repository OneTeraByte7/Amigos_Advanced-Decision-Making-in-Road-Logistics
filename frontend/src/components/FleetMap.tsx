import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet'
import { Icon } from 'leaflet'
import { FleetState } from '../types'
import 'leaflet/dist/leaflet.css'

const truckIcon = new Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <rect x="1" y="3" width="15" height="13"></rect>
      <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
      <circle cx="5.5" cy="18.5" r="2.5"></circle>
      <circle cx="18.5" cy="18.5" r="2.5"></circle>
    </svg>
  `),
  iconSize: [32, 32],
  iconAnchor: [16, 16],
})

const loadIcon = new Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="orange" stroke="white" stroke-width="2">
      <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
    </svg>
  `),
  iconSize: [28, 28],
  iconAnchor: [14, 14],
})

interface Props {
  fleetState: FleetState | null
}

export default function FleetMap({ fleetState }: Props) {
  const center: [number, number] = [20.5937, 78.9629]

  return (
    <MapContainer center={center} zoom={5} className="h-full w-full">
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      />
      
      {fleetState?.vehicles?.map(vehicle => {
        // Skip if coordinates are invalid
        if (!vehicle.current_location?.lat || !vehicle.current_location?.lng) return null;
        
        return (
          <Marker
            key={vehicle.vehicle_id}
            position={[vehicle.current_location.lat, vehicle.current_location.lng]}
            icon={truckIcon}
          >
            <Popup>
              <div className="font-sans">
                <h3 className="font-bold text-lg mb-2">{vehicle.vehicle_id}</h3>
                <div className="space-y-1 text-sm">
                  <p><span className="font-semibold">Location:</span> {vehicle.current_location.name || 'Unknown'}</p>
                  <p><span className="font-semibold">Status:</span> 
                    <span className={`ml-2 px-2 py-0.5 rounded-full text-xs ${
                      vehicle.status === 'idle' ? 'bg-gray-200 text-gray-700' :
                      vehicle.status.includes('en_route') ? 'bg-green-200 text-green-700' :
                      'bg-yellow-200 text-yellow-700'
                    }`}>
                      {vehicle.status}
                    </span>
                  </p>
                  <p><span className="font-semibold">Capacity:</span> {vehicle.capacity_tons?.toFixed(1) || 0} tons</p>
                  <p><span className="font-semibold">Current Load:</span> {vehicle.current_load_tons?.toFixed(1) || 0} tons</p>
                </div>
              </div>
            </Popup>
          </Marker>
        );
      })}

      {fleetState?.loads?.filter(l => l.status === 'available').map(load => {
        // Skip if coordinates are invalid
        if (!load.origin?.lat || !load.origin?.lng) return null;
        
        return (
          <Marker
            key={load.load_id}
            position={[load.origin.lat, load.origin.lng]}
            icon={loadIcon}
          >
            <Popup>
              <div className="font-sans">
                <h3 className="font-bold text-lg mb-2">{load.load_id}</h3>
                <div className="space-y-1 text-sm">
                  <p><span className="font-semibold">Origin:</span> {load.origin.name || 'Unknown'}</p>
                  <p><span className="font-semibold">Destination:</span> {load.destination.name || 'Unknown'}</p>
                  <p><span className="font-semibold">Weight:</span> {load.weight_tons} tons</p>
                  <p><span className="font-semibold">Distance:</span> {load.distance_km.toFixed(0)} km</p>
                  <p><span className="font-semibold">Revenue:</span> ${(load.offered_rate_per_km * load.distance_km).toFixed(0)}</p>
                </div>
              </div>
            </Popup>
          </Marker>
        );
      })}

      {fleetState?.trips?.map(trip => {
        const vehicle = fleetState?.vehicles?.find(v => v.vehicle_id === trip.vehicle_id)
        const load = fleetState?.loads?.find(l => l.load_id === trip.load_id)
        if (!vehicle || !load || !load.origin?.lat || !load.destination?.lat) return null

        return (
          <Polyline
            key={trip.trip_id}
            positions={[
              [load.origin.lat, load.origin.lng],
              [load.destination.lat, load.destination.lng]
            ]}
            color="blue"
            weight={3}
            opacity={0.6}
            dashArray="10, 10"
          />
        )
      })}
    </MapContainer>
  )
}