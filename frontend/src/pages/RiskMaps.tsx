import * as React from 'react';
import { MapContainer, TileLayer, Popup, Circle, LayersControl } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { MapPin, AlertTriangle, Flame, Info } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';

// Fix Leaflet's default icon path issues in React
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const defaultCenter: [number, number] = [40.7128, -74.0060]; // NYC

const riskZones = [
  { id: 1, center: [40.7128, -74.0060] as [number, number], radius: 2000, risk: 'high', label: 'Financial District' },
  { id: 2, center: [40.7580, -73.9855] as [number, number], radius: 1500, risk: 'medium', label: 'Times Square' },
  { id: 3, center: [40.7829, -73.9654] as [number, number], radius: 3000, risk: 'low', label: 'Central Park Area' },
];

const getColor = (risk: string) => {
  if (risk === 'high') return '#EF4444';
  if (risk === 'medium') return '#F59E0B';
  return '#22C55E';
};

// Heat Matrix 3x3 (Impact vs Probability)
interface MatrixCell {
  prob: 'Low' | 'Medium' | 'High';
  impact: 'Low' | 'Medium' | 'High';
  count: number;
  color: string;
  items: string[];
  action: string;
}

const HEAT_MATRIX: MatrixCell[] = [
  // High Impact
  { prob: 'Low', impact: 'High', count: 3, color: 'bg-amber-500/20 text-amber-600 border-amber-500/30', items: ['Counterparty Insolvency', 'Cyber Extortion'], action: 'Hedge via credit derivatives' },
  { prob: 'Medium', impact: 'High', count: 6, color: 'bg-rose-500/30 text-rose-600 border-rose-500/40', items: ['Commercial Real Estate Downgrades', 'Refinancing Squeeze'], action: 'Trigger liquidity buffer reserve' },
  { prob: 'High', impact: 'High', count: 9, color: 'bg-rose-600 text-white border-rose-700', items: ['Unhedged Rate Volatility', 'High DTI Defaults'], action: 'Mandate immediate credit cap ceiling' },
  // Medium Impact
  { prob: 'Low', impact: 'Medium', count: 1, color: 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20', items: ['Regional Transit Delay'], action: 'Routine monitoring' },
  { prob: 'Medium', impact: 'Medium', count: 4, color: 'bg-amber-500/20 text-amber-600 border-amber-500/30', items: ['Supplier Lead Time Lag', 'FX Volatility'], action: 'Re-negotiate vendor SLAs' },
  { prob: 'High', impact: 'Medium', count: 7, color: 'bg-rose-500/30 text-rose-600 border-rose-500/40', items: ['Consumer Delinquency Tick'], action: 'Proactive collection outreach' },
  // Low Impact
  { prob: 'Low', impact: 'Low', count: 0, color: 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20', items: ['Routine Hardware Wear'], action: 'Scheduled maintenance' },
  { prob: 'Medium', impact: 'Low', count: 2, color: 'bg-emerald-500/20 text-emerald-700 border-emerald-500/30', items: ['Short-term Cloud Latency'], action: 'Auto-scaling policy' },
  { prob: 'High', impact: 'Low', count: 5, color: 'bg-amber-500/20 text-amber-600 border-amber-500/30', items: ['Staff Turnover Seasonality'], action: 'Cross-training talent reserve' },
];

export function RiskMaps() {
  const [activeTab, setActiveTab] = React.useState('matrix');
  const [selectedCell, setSelectedCell] = React.useState<MatrixCell>(HEAT_MATRIX[2]);

  return (
    <div className="space-y-6 animate-in h-full flex flex-col">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-50">Risk Maps & Heat Matrix</h1>
            <Badge variant="outline" className="border-primary/40 text-primary font-mono text-xs">
              ISO 31000 Compliant
            </Badge>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Enterprise 3×3 Probability-Impact Risk Heat Map and Geospatial Monitored Exposure Zones.
          </p>
        </div>
        <div className="flex gap-1.5 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg text-xs">
          <button
            onClick={() => setActiveTab('matrix')}
            className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
              activeTab === 'matrix' ? 'bg-primary text-white shadow-sm' : 'text-slate-600 dark:text-slate-400'
            }`}
          >
            3×3 Heat Matrix
          </button>
          <button
            onClick={() => setActiveTab('geo')}
            className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
              activeTab === 'geo' ? 'bg-primary text-white shadow-sm' : 'text-slate-600 dark:text-slate-400'
            }`}
          >
            Geospatial Map
          </button>
        </div>
      </div>

      {activeTab === 'matrix' ? (
        <div className="grid gap-6 lg:grid-cols-12">
          {/* Matrix Visualizer */}
          <div className="lg:col-span-8">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2">
                  <Flame className="h-4 w-4 text-rose-500" /> Enterprise Risk Heat Matrix (Impact vs Probability)
                </CardTitle>
                <CardDescription className="text-xs">
                  Click any cell to inspect constituent risk drivers and recommended mitigation actions
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex">
                    <div className="w-20 text-xs font-semibold text-slate-400 flex items-center justify-center -rotate-90">
                      Impact
                    </div>
                    <div className="flex-1 space-y-2">
                      {['High', 'Medium', 'Low'].map((impactLevel) => (
                        <div key={impactLevel} className="grid grid-cols-3 gap-2">
                          {['Low', 'Medium', 'High'].map((probLevel) => {
                            const cell = HEAT_MATRIX.find(c => c.impact === impactLevel && c.prob === probLevel)!;
                            const isSelected = selectedCell.impact === cell.impact && selectedCell.prob === cell.prob;
                            return (
                              <button
                                key={probLevel}
                                onClick={() => setSelectedCell(cell)}
                                className={`h-24 rounded-xl border p-3 text-left transition-all flex flex-col justify-between ${cell.color} ${
                                  isSelected ? 'ring-2 ring-primary ring-offset-2 dark:ring-offset-slate-900 scale-[1.02] shadow-md' : 'hover:opacity-90'
                                }`}
                              >
                                <div className="flex items-center justify-between text-[11px] font-semibold">
                                  <span>{cell.impact} Impact</span>
                                  <Badge className="text-[10px] px-1.5 py-0 bg-black/20 text-inherit border-none">
                                    {cell.items.length} Risks
                                  </Badge>
                                </div>
                                <div className="text-[11px] font-mono">
                                  {cell.prob} Prob
                                </div>
                              </button>
                            );
                          })}
                        </div>
                      ))}
                      <div className="grid grid-cols-3 gap-2 text-center text-xs font-semibold text-slate-400 pt-2">
                        <span>Low Probability</span>
                        <span>Medium Probability</span>
                        <span>High Probability</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Cell Detail Drawer */}
          <div className="lg:col-span-4 space-y-4">
            <Card className="border-l-4 border-l-primary">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">Cell Deep Dive</CardTitle>
                  <Badge variant="outline" className="text-xs font-mono">
                    {selectedCell.impact} / {selectedCell.prob}
                  </Badge>
                </div>
                <CardDescription className="text-xs">Active risks in selected exposure regime</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Identified Risk Drivers</span>
                  <div className="space-y-1.5">
                    {selectedCell.items.map((it, i) => (
                      <div key={i} className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 text-xs font-medium text-slate-900 dark:text-slate-100 flex items-center gap-2">
                        <AlertTriangle className="h-3.5 w-3.5 text-amber-500 shrink-0" />
                        {it}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-primary/5 dark:bg-primary/10 border border-primary/20 space-y-1.5">
                  <span className="text-xs font-semibold uppercase tracking-wider text-primary flex items-center gap-1.5">
                    <Info className="h-3.5 w-3.5" /> Prescribed Action
                  </span>
                  <p className="text-xs text-slate-700 dark:text-slate-200 leading-relaxed font-medium">
                    {selectedCell.action}
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-4 flex-1">
          {/* Map Panel */}
          <div className="lg:col-span-3 h-full min-h-[500px]">
            <Card className="h-full flex flex-col overflow-hidden">
              <CardContent className="p-0 flex-1 relative">
                <MapContainer 
                  center={defaultCenter} 
                  zoom={12} 
                  className="h-full w-full absolute inset-0 z-0"
                >
                  <LayersControl position="topright">
                    <LayersControl.BaseLayer checked name="OpenStreetMap">
                      <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                      />
                    </LayersControl.BaseLayer>
                    <LayersControl.BaseLayer name="Dark Matter (CartoDB)">
                      <TileLayer
                        attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
                        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                      />
                    </LayersControl.BaseLayer>

                    <LayersControl.Overlay checked name="Risk Zones">
                      <React.Fragment>
                        {riskZones.map(zone => (
                          <Circle
                            key={zone.id}
                            center={zone.center}
                            radius={zone.radius}
                            pathOptions={{ color: getColor(zone.risk), fillColor: getColor(zone.risk), fillOpacity: 0.4 }}
                          >
                            <Popup>
                              <strong>{zone.label}</strong><br />
                              Risk Level: {zone.risk}
                            </Popup>
                          </Circle>
                        ))}
                      </React.Fragment>
                    </LayersControl.Overlay>
                  </LayersControl>
                  
                  {/* Overlay controls for UI on top of map */}
                  <div className="absolute bottom-6 left-6 z-[400] bg-white dark:bg-slate-900 p-4 rounded-lg shadow-lg border border-slate-200 dark:border-slate-800">
                    <h4 className="font-semibold text-sm mb-2">Legend</h4>
                    <div className="space-y-2 text-xs">
                      <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-danger opacity-60"></div> High Risk</div>
                      <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-warning opacity-60"></div> Medium Risk</div>
                      <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-success opacity-60"></div> Low Risk</div>
                    </div>
                  </div>
                </MapContainer>
              </CardContent>
            </Card>
          </div>

          {/* Info Panel */}
          <div className="lg:col-span-1 space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><MapPin className="h-5 w-5" /> Regions</CardTitle>
                <CardDescription>Active monitored zones</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {riskZones.map(zone => (
                  <div key={zone.id} className="p-3 border rounded-md border-slate-100 dark:border-slate-800">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium text-sm">{zone.label}</span>
                      <Badge variant={zone.risk === 'high' ? 'destructive' : zone.risk === 'medium' ? 'warning' : 'success'}>
                        {zone.risk}
                      </Badge>
                    </div>
                    <div className="text-xs text-slate-500">
                      Radius: {zone.radius / 1000}km
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
