export interface IogpRuleMetadata {
  id: string;
  name: string;
  shortCode: string;
  iconName: string;
  category: string;
  description: string;
  mandatoryRequirements: string[];
}

export const IOGP_LIFE_SAVING_RULES: Record<string, IogpRuleMetadata> = {
  'Energy Isolation': {
    id: 'LSR-01',
    name: 'Energy Isolation',
    shortCode: 'EI',
    iconName: 'ZapOff',
    category: 'Hazardous Energy',
    description: 'Verify isolation and zero energy state before work begins.',
    mandatoryRequirements: [
      'Identify all energy sources (electrical, mechanical, hydraulic, chemical).',
      'Isolate, lock out, tag out and test for zero energy.',
      'Obtain required permit to work before starting isolation work.'
    ]
  },
  'Hot Work': {
    id: 'LSR-02',
    name: 'Hot Work',
    shortCode: 'HW',
    iconName: 'Flame',
    category: 'Fire & Explosion',
    description: 'Control flammables and ignition sources in hazardous zones.',
    mandatoryRequirements: [
      'Conduct gas testing before and during hot work.',
      'Clear flammables within minimum safety distance.',
      'Ensure a trained fire watch is present with appropriate firefighting equipment.'
    ]
  },
  'Confined Space': {
    id: 'LSR-03',
    name: 'Confined Space',
    shortCode: 'CS',
    iconName: 'Box',
    category: 'Toxic & Asphyxiating Atmospheres',
    description: 'Obtain authorization and verify atmospheric conditions before entry.',
    mandatoryRequirements: [
      'Atmosphere tested and continuously monitored for oxygen and toxic gases.',
      'Standby attendant posted at the entrance at all times.',
      'Rescue plan and emergency communication verified.'
    ]
  },
  'Line of Fire': {
    id: 'LSR-04',
    name: 'Line of Fire',
    shortCode: 'LF',
    iconName: 'Crosshair',
    category: 'Kinetic & Mechanical Energy',
    description: 'Position yourself and others outside danger zones and stored energy paths.',
    mandatoryRequirements: [
      'Never stand under suspended loads or between moving equipment.',
      'Ensure barricades and exclusion zones are maintained.',
      'Stay visible to equipment operators at all times.'
    ]
  },
  'Working at Height': {
    id: 'LSR-05',
    name: 'Working at Height',
    shortCode: 'WH',
    iconName: 'ArrowUpCircle',
    category: 'Falls from Height',
    description: 'Protect yourself against falls when working at height (above 1.8m).',
    mandatoryRequirements: [
      'Inspect fall arrest systems and anchor points prior to use.',
      'Maintain 100% tie-off at all times when outside protected platforms.',
      'Prevent dropped objects using tool lanyards and toe-boards.'
    ]
  },
  'Bypassing Safety Controls': {
    id: 'LSR-06',
    name: 'Bypassing Safety Controls',
    shortCode: 'BSC',
    iconName: 'ShieldAlert',
    category: 'Critical Safety Systems',
    description: 'Obtain authorization before overriding or disabling safety critical equipment.',
    mandatoryRequirements: [
      'Identify safety-critical alarms, trips, ESDs, or relief devices.',
      'Obtain formal management override approval.',
      'Implement compensating temporary barriers while safety control is bypassed.'
    ]
  },
  'Safe Mechanical Lifting': {
    id: 'LSR-07',
    name: 'Safe Mechanical Lifting',
    shortCode: 'SML',
    iconName: 'Anchor',
    category: 'Rigging & Cranes',
    description: 'Plan and execute lifting operations with certified equipment and personnel.',
    mandatoryRequirements: [
      'Verify crane and rigging gear inspection certificates.',
      'Ensure lift plan matches load weight and center of gravity.',
      'Establish exclusion radius under the lift path.'
    ]
  },
  'Driving': {
    id: 'LSR-08',
    name: 'Driving',
    shortCode: 'DRV',
    iconName: 'Truck',
    category: 'Transport Safety',
    description: 'Follow journey management and road safety rules.',
    mandatoryRequirements: [
      'Always wear seatbelts and adhere to speed limits.',
      'Do not use mobile phones while driving.',
      'Complete pre-trip vehicle safety inspection.'
    ]
  },
  'Work Authorization': {
    id: 'LSR-09',
    name: 'Work Authorization',
    shortCode: 'WA',
    iconName: 'FileCheck',
    category: 'Permit to Work',
    description: 'Work with a valid permit when required and understand all controls.',
    mandatoryRequirements: [
      'Verify permit conditions, gas checks, and isolations prior to job start.',
      'Conduct a Job Safety Analysis (JSA) toolbox briefing.',
      'Stop work immediately if site conditions change.'
    ]
  }
};
