import { Routes } from '@angular/router';
import { TopicsListComponent } from './pages/topics-list/topics-list.component';
import { DebateViewComponent } from './pages/debate-view/debate-view.component';

export const routes: Routes = [
    { path: '', component: TopicsListComponent },
    { path: 'debates/:id', component: DebateViewComponent },
    { path: '**', redirectTo: '' } // Redirect any other path to home
];
