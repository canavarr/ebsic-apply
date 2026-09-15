/**
 * EBS Investment Club — Stock Analysis Workshop (ebsic.ee/workshop/)
 *
 * Firebase web config for the live claims board. Published deliberately: a
 * browser must receive these values to reach Firestore, so they are public on
 * any deployed page regardless. Writes are constrained by the Firestore rules,
 * and the key should carry an HTTP referrer restriction to ebsic.ee.
 */
window.IC_WORKSHOP_CONFIG = {
  firebase: {
    apiKey: "AIzaSyCn14E-Ex_79Wf14va1ilLoM1WcGj7AXmw",
    authDomain: "ic-workshop-c7938.firebaseapp.com",
    projectId: "ic-workshop-c7938",
    storageBucket: "ic-workshop-c7938.firebasestorage.app",
    messagingSenderId: "601965176639",
    appId: "1:601965176639:web:e7db567a5b80341cbc158a",
  },
};
