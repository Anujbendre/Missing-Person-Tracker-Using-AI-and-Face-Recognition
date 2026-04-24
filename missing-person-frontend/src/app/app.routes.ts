import { Routes } from '@angular/router';

import { Dashboard } from './pages/dashboard/dashboard';
import { AboutSystem } from './pages/about-system/about-system';
import { HowItWorks } from './pages/how-it-works/how-it-works';
import { FAQs } from './pages/faqs/faqs';
import { SignupComponent } from './pages/signup/signup';
import { CitizenDashboardComponent } from './pages/citizen-dashboard/citizen-dashboard';
import { ReportMissingComponent } from './pages/report-missing/report-missing';
import { ViewMissingComponent } from './pages/view-missing/view-missing';
import { ApplyFIRComponent } from './pages/apply-fir/apply-fir';
import { MyCasesComponent } from './pages/my-cases/my-cases';
import { DownloadFIRComponent } from './pages/download-fir/download-fir';
import { PoliceDashboardComponent } from './pages/police-dashboard/police-dashboard';
import { PoliceCasesComponent } from './pages/police-cases/police-cases';
import { CctvComponent } from './pages/cctv/cctv'; // ✅ FIXED

import { policeGuard } from './auth/auth-guard';
import { PoliceLoginComponent } from './pages/police-login/police-login';
import { PoliceSignupComponent } from './pages/police-signup/police-signup';
import { ViewFirComponent } from './pages/view-fir/view-fir';
import { AiRecognitionComponent } from './pages/ai-recognition/ai-recognition';
import { CaseTimelineComponent } from './pages/case-timeline/case-timeline';

export const routes: Routes = [

  { path: '', component: Dashboard },

  { path: 'about-system', component: AboutSystem },

  { path: 'how-it-works', component: HowItWorks },

  { path: 'faqs', component: FAQs },

  // { path: 'signup', component: SignupComponent },

  { path: 'dashboard', component: CitizenDashboardComponent },

  { path: 'report-missing', component: ReportMissingComponent },

  { path: 'view-missing', component: ViewMissingComponent },

  { path: 'apply-fir', component: ApplyFIRComponent },

  { path: 'my-cases', component: MyCasesComponent },

  { path: 'download-fir', component: DownloadFIRComponent },

  // ✅ Police routes with guard
  { path: 'police-dashboard', component: PoliceDashboardComponent, canActivate: [policeGuard] },
  { path: 'police-cases', component: PoliceCasesComponent, canActivate: [policeGuard] },
  { path: 'case-timeline/:id', component: CaseTimelineComponent, canActivate: [policeGuard] },
  { path: 'cctv', component: CctvComponent, canActivate: [policeGuard] },
  { path: 'view-fir', component: ViewFirComponent, canActivate: [policeGuard] },
  { path: 'ai-recognition', component: AiRecognitionComponent, canActivate: [policeGuard] },

  
  { path: 'police-login', component: PoliceLoginComponent },
  { path: 'police-signup', component: PoliceSignupComponent },

];