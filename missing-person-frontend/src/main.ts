import { bootstrapApplication } from '@angular/platform-browser';
import { App } from './app/app';

import { provideRouter } from '@angular/router';
import { routes } from './app/app.routes';

import { provideHttpClient } from '@angular/common/http';
import { importProvidersFrom } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';

bootstrapApplication(App, {
  providers: [
    provideRouter(routes),
    provideHttpClient(),

    // 🌐 Translate (optional but correct)
    importProvidersFrom(
      TranslateModule.forRoot()
    )
  ]
}).catch(err => console.error(err));