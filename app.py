import streamlit as st
from datetime import datetime

st.set_page_config(page_title='Marley Coffee | Hub B2B · Demo', page_icon='☕', layout='wide')
st.markdown('''<style>.stApp{background:#F5F3EF;color:#241C18}h1,h2,h3{color:#241C18}div.stButton>button[kind="primary"]{background:#3E2723;color:white;border:0} .stMetric{background:#fff;padding:12px;border-radius:12px}</style>''', unsafe_allow_html=True)

PRODUCTS = {'Café en grano 1 kg': 18900, 'Café molido 500 g': 10900, 'Cápsulas (caja)': 8900}
MACHINES = ['Máquina OCS - Oficina Central', 'Máquina OCS - Sala de reuniones']

def init():
    defaults = {'role':None,'page':'Inicio','cart':{},'cart_version':0,'orders':[{'id':'PED-001','fecha':'2026-09-12','detalle':'Café en grano 1 kg × 4','estado':'Entregado'}], 'tickets':[{'id':'OCS-001','equipo':MACHINES[0],'detalle':'Revisión preventiva (ejemplo)','estado':'Cerrado'}]}
    for key,val in defaults.items():
        if key not in st.session_state: st.session_state[key]=val
init()

st.caption('PROTOTIPO ACADÉMICO · DATOS FICTICIOS · SIN CONEXIÓN A MARLEY COFFEE NI DICALLA SPA')
st.title('☕ Marley Coffee | Hub de Autogestión B2B')
st.write('Demostración funcional de portal web responsive para HORECA y OCS.')

if st.session_state.role is None:
    st.subheader('Acceso de demostración')
    with st.form('login'):
        role = st.selectbox('Perfil de cliente', ['HORECA — Restaurante / cafetería', 'OCS — Oficina / empresa'])
        company = st.text_input('Empresa (ficticia)', value='Cliente de demostración')
        st.caption('No ingreses RUT ni contraseñas reales. Este acceso es solo una simulación.')
        submit=st.form_submit_button('Ingresar al portal', type='primary')
    if submit:
        st.session_state.role='HORECA' if role.startswith('HORECA') else 'OCS'
        st.session_state.company=company
        st.session_state.page='Inicio'
        st.rerun()
    st.stop()

with st.sidebar:
    st.subheader(st.session_state.company)
    st.caption('Perfil: '+st.session_state.role)
    menu = ['Inicio','Reposición','Historial'] if st.session_state.role=='HORECA' else ['Inicio','Reportar falla','Seguimiento']
    page=st.radio('Navegación', menu, index=menu.index(st.session_state.page) if st.session_state.page in menu else 0)
    st.session_state.page=page
    if st.button('Cerrar sesión'):
        st.session_state.role=None
        st.session_state.page='Inicio'
        st.rerun()

role=st.session_state.role
page=st.session_state.page
if role=='HORECA':
    if page=='Inicio':
        st.header('Dashboard HORECA')
        a,b,c=st.columns(3)
        a.metric('Pedidos de ejemplo',len(st.session_state.orders))
        b.metric('Productos disponibles',len(PRODUCTS))
        c.metric('Carrito actual',sum(st.session_state.cart.values()))
        st.info('Este panel simula el acceso a reposición e historial del cliente empresa.')
        if st.button('Ir a reposición',type='primary'):
            st.session_state.page='Reposición';st.rerun()
    elif page=='Reposición':
        st.header('Reposición HORECA')
        st.write('Modifica cantidades y confirma un pedido de prueba. No se realizará ninguna compra real.')
        with st.form('cart_form'):
            qty={}
            for product,price in PRODUCTS.items():
                qty[product]=st.number_input(f'{product} · Precio ficticio ${price:,} CLP'.replace(',','.'),min_value=0,max_value=100,value=st.session_state.cart.get(product,2 if product=='Café en grano 1 kg' else 0),step=1,key=f'qty_{st.session_state.cart_version}_{list(PRODUCTS).index(product)}')
            update=st.form_submit_button('Actualizar carrito')
        if update:
            st.session_state.cart=qty.copy()
            st.rerun()
        total=sum(PRODUCTS[p]*q for p,q in st.session_state.cart.items())
        st.subheader('Resumen del carrito')
        for p,q in st.session_state.cart.items():
            if q:
                st.write(f'{p}: {q} × ${PRODUCTS[p]:,.0f} = ${PRODUCTS[p]*q:,.0f}'.replace(',','.'))
        st.metric('Total ilustrativo (CLP)',f'${total:,.0f}'.replace(',','.'))
        if st.button('Confirmar pedido simulado',type='primary',disabled=total==0):
            details=', '.join(f'{p} × {q}' for p,q in st.session_state.cart.items() if q)
            order_id=f'PED-{len(st.session_state.orders)+1:03d}'
            st.session_state.orders.insert(0,{'id':order_id,'fecha':datetime.now().strftime('%Y-%m-%d'),'detalle':details,'estado':'Recibido (simulado)'})
            st.session_state.cart={}
            st.session_state.cart_version+=1
            st.success(f'Pedido de prueba {order_id} registrado. Consulta el historial.')
    else:
        st.header('Historial de pedidos')
        st.dataframe(st.session_state.orders,use_container_width=True,hide_index=True)
        st.caption('Las facturas y documentos contables reales requerirían integración con el ERP.')
else:
    if page=='Inicio':
        st.header('Estado de equipos OCS')
        st.info('Estados de ejemplo; no existe telemetría ni conexión a máquinas reales.')
        for machine in MACHINES:
            with st.container(border=True):
                st.subheader('☕ '+machine)
                st.write('Estado ilustrativo: operativo / pendiente de verificación')
        if st.button('Reportar una incidencia',type='primary'):
            st.session_state.page='Reportar falla';st.rerun()
    elif page=='Reportar falla':
        st.header('Reportar falla OCS')
        with st.form('ticket'):
            machine=st.selectbox('Equipo',MACHINES)
            problem=st.selectbox('Tipo de incidencia',['No dispensa café','No enciende','Fuga de agua','Otro'])
            detail=st.text_area('Descripción (sin datos personales)')
            send=st.form_submit_button('Crear ticket simulado',type='primary')
        if send:
            ticket_id=f'OCS-{len(st.session_state.tickets)+1:03d}'
            st.session_state.tickets.insert(0,{'id':ticket_id,'equipo':machine,'detalle':problem+(' — '+detail if detail else ''),'estado':'Recibido (simulado)'})
            st.success(f'Ticket {ticket_id} creado. Revisa Seguimiento.')
    else:
        st.header('Seguimiento de tickets')
        st.dataframe(st.session_state.tickets,use_container_width=True,hide_index=True)
        st.caption('Los estados se almacenan solo en esta sesión; no se envían a un proveedor técnico.')

st.divider()
st.caption('Proyecto académico · Duoc UC · Marley Coffee / Dicalla SpA (caso de estudio). MVP de demostración, no servicio oficial.')
