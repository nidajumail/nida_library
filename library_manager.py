import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import random
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie  # for loading lottie animations
import requests


st.set_page_config(
    page_title = "Personal Library Management System",
    page_icon = "📚",
    layout = "wide",
    initial_sidebar_state="unexpanded"
    )


# custom css for styling the app
st.markdown("""
<style>
    .main-header{
        font-size:3rem | important;
        color:#1A3A8A;
        font-weight:700;
        margin-bottom:1rem;
        text-align:center;
        text-shadow:2px 2px 4px rgba(0,0,0 0.1)
            }
    .sub-header{
        font-size:1.8rem | important;
        color:#3B82F6;
        font-weight:600;
        margin-bottom:1rem;
        margin-top:1rem;}
    .success-message{
        padding:1rem;
        background-color:#ECFDf5
        border-left: 5pxsolid #10B981;
        border-radius: 0.375;
        
            }
    .warning-message{
        padding:1rem;
        background-color:#FEF3C7
        border-left: 5pxsolid #F59E0B;
        border-radius: 0.375;
            }
    .book-card{
        background-color:#F9FAFB;   
        border-radius: 0.375rem;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
            }  
    .book-card:hover{
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);  
        transform: translateY(-5px);
        }
    .read-badge{
        background-color:#10B981;
        color:white;
        padding: 0.5rem;
        border-radius: 0.375rem;
        font-size: 0.875rem;
        font-weight: 600;    
            }        
    .unread-badge{
        background-color:#F59E0B;   
        color:white;
        padding: 0.5rem;
        border-radius: 0.375rem;
        font-size: 0.875rem;    
        font-weight: 600;
            }
    # .reading-badge{
    #     background-color:#3B82F6;
    #     color:white;
    #     padding: 0.5rem;
    #     border-radius: 0.375rem;
    #     font-size: 0.875rem;
    #     font-weight: 600;
    #         }
    .book-title{
        font-size: 1.5rem;
        font-weight: 700;
        color: #1A3A8A;
            }
    .action-button{ 
        margin-right: 0.5rem;
            }
    .Button>button{   
        border-radius: 0.375rem;
            }
    </style>.""", unsafe_allow_html=True)
            
                    
def load_lottieurl(url):
    try:
              r = requests.get(url)
              if r.status_code != 200:
                return None
              return r.json()
    except:
              return None

if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_removed' not in st.session_state:
     st.session_state.book_removed = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'home'  


def load_library():
    try:
        if os.path.exists('library.json'):
            with open('library.json','r') as file:
                 st.session_state.library = json.load(file)
                 return True
            return False
    except Exception as e:
         st.error(f"Error loading library:{e}")
         return False   
    #save library
def save_library():
    try:
        with open('library.json','w')as file:
             json.dump(st.session_state.library,file)
             return True
    except Exception as e:
        st.error(f"Error loading library:{e}")
        return False
    

def add_book(title,author,publication_year,genre, read_status):
     book = {
            'title': title,
            'author': author,
            'publication_year': publication_year,
            'genre': genre,
            'read_status': read_status,
            'added_on': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
             
     st.session_state.library.append(book)
     save_library()
     st.session_state.book_added = True
     time.sleep(0.5)#animation delay

     #remove book
def remove_book(index):
     if 0 <= index < len(st.session_state.library):
          
          del st.session_state.library [index]
          save_library()
          st.session_state.book_removed = True
          return True
     return False


def search_books(serach_term, search_by):
    search_term = serach_term.lower()
    results = []
        
    for book in st.session_state.library:
         if search_by == 'title' and search_term in book['title'].lower():
              results.append(book)
         elif search_by == 'author' and search_term in book['author'].lower():
              results.append(book)      
         elif search_by == 'genre' and search_term in book['genre'].lower():
              results.append(book)
         st.session_state.search_results = results   

       #calculate lubrary stats  
def get_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book['read_status'] == 'read')
    percent_read = (read_books / total_books * 100) if total_books > 0 else 0

    genres = {}
    authors = {}
    decades = {}
    
    for book in st.session_state.library:
         if book['genre'] in genres:
                genres[book['genre']] += 1
         else:
                genres[book['genre']] = 1

        #count authors   
         decades = book['publication_year'] // 10 * 10
         if decades in decades:
            decades[decades] += 1
         else:
            decades[decades] = 1
   
    genres = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))
    authors = dict(sorted(authors.items(), key=lambda x: x[1], reverse=True))
    decades = dict(sorted(decades.items(), key=lambda x: x[0]))
    return {
        'total_books': total_books,
        'read_books': read_books,
        'percent_read': percent_read,
        'genres': genres,
        'authors': authors,
        'decades': decades

    }
def create_visualizations(stats):
     if stats['total_books'] > 0:
         fig_read_status = go.figure{data=[go.pie(
             labels=['Read', 'Unread'],
             values=[stats['read_books'], stats['total_books'] - stats['read_books']],
             hole=0.4
             marker=dict(colors=['#10B981', '#F59E0B'])
         )],}
         fig_read_status.update_layout(
                 title_text='Read vs Unread Books',     
                 showlegend=True,
                 height=400,
                 width=400,
                 )
         st.plotly_chart(fig_read_status, use_container_width=True)
         #barChart for genres
     if stats['genres']:
          genres_df = pd.DataFrame({
               'Genre': list(stats['genres'].keys()),
               'Count': list(stats['genres'].values())
          })
          fig_genres = px.bar(
                 genres_df,
                   x='Genre',
                   y='Count', 
                   color='Count',            
                   color_continuous_scale=px.colors.sequential.Blues,)
          fig_genres.update_layout(
                    title_text='Books by Genre',
                    xaxis_title='Genre',
                    yaxis_title='Number of Books',
                    height=400,
                    width=400,
                    )
          st.plotly_chart(fig_genres, use_container_width=True)
          if stats['decades']:
                decades_df = pd.DataFrame({
                      'Decade': list(stats['decades'].keys()),
                      'Count': list(stats['decades'].values())
                })
                fig_decades = px.line(
                        decades_df,
                        x='Decade',
                        y='Count',
                        markers=True,
                        line_shape='spline',
                        )
                
                fig_decades.update_layout(
                      title_text='Books by Genre',
                    xaxis_title='Genre',
                    yaxis_title='Number of Books',
                    height=400,
                    width=400,
                    )
                st.plotly_chart(fig_decades, use_container_width=True)
        
#load library
if load_library():
    st.sidebar.markdown(
        """
        <style>
            .sidebar .sidebar-content{
                background-color:#F9FAFB;
                }
        </style>
        """, unsafe_allow_html=True)
    lottie_book=load_lottieurl('https://assets3.lottiefiles.com/packages/lf20_2jzq4g.json')
    if lottie_book:
        st_lottie(lottie_book, speed=1, width=300, height=300, key="book")
    
    nav_options = st.sidebar.radio(
       " choose an options",
       ["View Library", "Add Book", "Search Books", "Library Stats"]
    )

    if nav_options == "View Library":
        st.session_state.current_view = 'library'
    elif nav_options == "Add Book":
        st.session_state.current_view = 'add_book'
    elif nav_options == "Search Books":
        st.session_state.current_view = 'search_books'
    elif nav_options == "Library Stats":
        st.session_state.current_view = 'library_stats'

    st.markdown(  "<h1 class ='main header'> Personal Library Manager </h1>", unsafe_allow_html=True)
    if st.session_state.current_view == " add":
         st.markdown("<h1 class  = 'sub-header'> Add a new book</h2>",unsafe_allow_html=True)


         #adding a books input form
         with st.form(key="add_book_form"):
              col1, col2 =st.columns(2)

              with col1:
                   title = st.text_input("Book Title", max_chars=100) 
                   author = st.text_input("Author", max_chars=100)
                   publication_year = st.number_input("Publication year",min_value=1000, max_value=datetime.now().year, step =1, value= 2023)
              with col2:
                   genre = st.selectbox("Genre",[
                        "Friction","Non-Friction","Science","Technology","History","Biography","Fantasy","Mystery","Romance","Horror","Self-Help","Poetry","Children's Books","Graphic Novels","Cookbooks","Travel"]
                     )  
                   read_status = st.selectbox("Read Status",["Read","Unread","Reading"],horizontal=True)
                   read_bool = read_status == "Read"
              submit_button = st.form_submit_button("Add Book")
    
              if submit_button and title and author:   
                   add_book(title, author, publication_year, genre, read_bool)
              if st.session_state.book_added:
                   st.markdown(" <div class='success-message'>Book added successfully!</div>" , unsafe_allow_html=True)
                   st.balloons()
                   st.session_state.book_added = False
    elif st.session_state.current_view == "library":
         st.markdown("<h1 class  = 'sub-header'> Your Library</h2>",unsafe_allow_html=True)

         if not st.session_state.library:
              st.markdown("<div class='warning-message'>Your library is empty. Please add books to your library.</div>", unsafe_allow_html=True)
         else:
            cols = st.columns(2)
            for i , book in enumerate(st.session_state.library):
                 with cols[i % 2]:
                      st.markdown(f"""<div class='book-card'>
                                  <h3>{book['title']}</h3>
                                  <p><strong>Author:</strong> {book['author']}</p>
                                  <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                                  <p><strong>Genre:</strong> {book['genre']}</p>
                                    <p><span class='{'read-badge' if book['read_status'] else 'unread-badge'}'>{'Read' if book['read_status'] else 'Unread'}</span></p>
</div>""", unsafe_allow_html=True)  

                      col1, col2 = st.columns(2)
                      with col1:
                           if st.button(f"Remove Book", key=f"remove_{i}",use_container_width=True):
                                if remove_book(i):
                                     st.session_state.book_removed = True
                                     st.session_state.library[i]['read_status']= False   
                                     save_library()
                                     st.rerun()
    if st.session_state.book_removed:  
         st.markdown("<div class='success-message'>Book removed successfully!</div>", unsafe_allow_html=True)
         st.session_state.book_removed = False
    elif st.session_state.current_view == "search_books":
         st.markdown("<h1 class  = 'sub-header'> Search for a book</h2>",unsafe_allow_html=True)      

         search_by = st.selectbox("Search by", ["Title", "Author", "Genre"])
         search_term = st.text_input("Enter search term")
        

         if st.button("Search", use_container_width=False):
              if search_term:
                   search_books(search_term, search_by.lower())
                   if st.session_state.search_results:
                    time.sleep(0.5)
                    search_books(search_term, search_by.lower())
                   if hasattr(st.session_state, 'search_results'):
                        if st.session_state.search_results:
                            st.markdown("<h2 class='sub-header'>Search Results</h2>", unsafe_allow_html=True)
                            for i, book in enumerate(st.session_state.search_results):
                                    st.markdown(f"""<div class='book-card'>
                                                <h3>{book['title']}</h3>
                                                <p><strong>Author:</strong> {book['author']}</p>
                                                <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                                                <p><strong>Genre:</strong> {book['genre']}</p>
                                                <p><span class='{'read-badge' if book['read_status'] else 'unread-badge'}'>{'Read' if book['read_status'] else 'Unread'}</span></p></div>""", unsafe_allow_html=True)
                        elif search_term:
                            st.markdown("<div class='warning-message'>No results found.</div>", unsafe_allow_html=True)
              elif st.session_state.current_view == "library_stats":
                   st.markdown("<h1 class  = 'sub-header'> Your Library Stats</h2>",unsafe_allow_html=True)

                   if not st.session_state.library:
                        st.markdown("<div class='warning-message'>Your library is empty. Please add books to your library.</div>", unsafe_allow_html=True)
                   else:
                        stats = get_library_stats()
                        col1, col2, col3 = st.columns(2)
                        with col1:
                             st.metric("Total Books", stats['total_books'])
                        with col2:
                             st.metric("Read Books", stats['read_books'])
                        with col3:             
                             st.metric("Percent Read", f"{stats['percent_read']:.2f}%")
                             create_visualizations()
                        if stats['authors']:
                             st.markdown("<h2 class='sub-header'>Top Authors</h2>", unsafe_allow_html=True)
                             top_authors = sorted(stats['authors'].items(), key=lambda x: x[1], reverse=True)[:5]
                             for author, count in top_authors:
                                  st.markdown(f"**{author}**: {count} books{'s' if count > 1 else ''}")
st.markdown("---")
st.markdown("copyright © 2025 Nida Haq Personal Library Manager. All rights reserved.", unsafe_allow_html=True)
                                  
                                  
                       
                   
