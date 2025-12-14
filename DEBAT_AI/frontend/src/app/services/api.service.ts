import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Debate, Message, SuggestionResponse} from '../models';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) { }

  getDebates(): Observable<Debate[]> {
    return this.http.get<Debate[]>(`${this.baseUrl}/debates`);
  }

  getMessages(debateId: number, sessionId: string): Observable<Message[]> {
    return this.http.get<Message[]>(`${this.baseUrl}/debates/${debateId}/messages?session_id=${sessionId}`);
  }

  postMessage(debateId: number, content: string, username: string, sessionId: string): Observable<Message> {
    return this.http.post<Message>(`${this.baseUrl}/debates/${debateId}/messages`, { content, username, session_id: sessionId });
  }

  getSuggestions(debateId: number, targetMessageId: number): Observable<SuggestionResponse> {
    return this.http.get<SuggestionResponse>(`${this.baseUrl}/debates/${debateId}/suggestions/${targetMessageId}`);
  }

  resetDebate(debateId: number, sessionId: string): Observable<any> {
    return this.http.delete(`${this.baseUrl}/debates/${debateId}/messages?session_id=${sessionId}`);
  }
}